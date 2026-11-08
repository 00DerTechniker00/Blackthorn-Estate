package de.blackthorn;

import java.io.*;
import java.net.URI;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;
import org.bukkit.*;
import org.bukkit.block.data.BlockData;
import org.bukkit.command.*;
import org.bukkit.event.*;
import org.bukkit.event.block.*;
import org.bukkit.plugin.java.JavaPlugin;

/** Reads world blocks on the server thread; only immutable snapshots cross to HTTP. */
public final class BlackthornLive extends JavaPlugin implements Listener {
    record Position(int x,int y,int z,BlockData expected) {}
    private final List<Position> positions = new ArrayList<>();
    private final Map<String,Integer> indices = new HashMap<>();
    private final Set<Integer> dirty = new LinkedHashSet<>();
    private byte[] states;
    private volatile String fingerprint, revision;
    private String token, endpoint;
    private volatile String lastUpload="Noch keine Übertragung";
    private World world;
    private int cursor, budget, ox, oy, oz;
    private long scanNanos;
    private final AtomicBoolean sending = new AtomicBoolean(), syncing = new AtomicBoolean();
    private volatile long lastSyncAttempt;
    private volatile String syncStatus="Noch kein Abgleich";
    private ExecutorService network;
    private HttpClient http;
    private String key(int x,int y,int z) { return x+","+y+","+z; }
    @Override public void onEnable() {
        saveDefaultConfig();
        try {
            token=getConfig().getString("write-token","");
            endpoint=getConfig().getString("endpoint","");
            URI uri=URI.create(endpoint);
            if(!"https".equals(uri.getScheme())||uri.getHost()==null||uri.getUserInfo()!=null||uri.getQuery()!=null||uri.getFragment()!=null||!uri.getPath().endsWith("/api/build-progress")||token.length()<32||token.contains("\n")||token.contains("\r"))
                throw new IllegalArgumentException("HTTPS-Endpoint und write-token (mindestens 32 Zeichen) konfigurieren.");
            world=Bukkit.getWorld(getConfig().getString("world","world"));
            if(world==null)throw new IllegalArgumentException("Konfigurierte Welt nicht gefunden.");
            ox=getConfig().getInt("offset-x");oy=getConfig().getInt("offset-y");oz=getConfig().getInt("offset-z");
            budget=Math.max(1,Math.min(2000,getConfig().getInt("positions-per-tick",300)));
            scanNanos=Math.max(1,Math.min(10,getConfig().getInt("max-scan-millis-per-tick",2)))*1_000_000L;
            network=Executors.newSingleThreadExecutor(task->{Thread thread=new Thread(task,"BlackthornLive-sync");thread.setDaemon(true);return thread;});
            http=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(8)).followRedirects(HttpClient.Redirect.NEVER).build();
            byte[] embedded;try(var resource=Objects.requireNonNull(getResource("plan.tsv.gz"))){embedded=resource.readAllBytes();}
            Path cached=getDataFolder().toPath().resolve("current-plan.tsv.gz");
            try{installPlan(PlanData.decode(Files.exists(cached)?Files.readAllBytes(cached):embedded));}
            catch(Exception e){getLogger().warning("Gespeicherter Plan nicht nutzbar, verwende eingebauten Plan.");installPlan(PlanData.decode(embedded));}
            Bukkit.getPluginManager().registerEvents(this,this);
            Bukkit.getScheduler().runTaskTimer(this,this::scan,1,1);
            long period=Math.max(5,getConfig().getInt("upload-seconds",10))*20L;
            Bukkit.getScheduler().runTaskTimer(this,this::upload,period,period);
            long syncPeriod=Math.max(30,getConfig().getInt("sync-seconds",60))*20L;
            Bukkit.getScheduler().runTaskTimer(this,()->syncPlan(false),syncPeriod,syncPeriod);
            syncPlan(true);
            getLogger().info(positions.size()+" Positionen geladen. Nur geladene Chunks werden gelesen; Welt wird nicht verändert.");
        }catch(Exception e){getLogger().severe("Start fehlgeschlagen: "+e.getMessage());Bukkit.getPluginManager().disablePlugin(this);}
    }
    private void check(int i){
        Position p=positions.get(i);
        if(!world.isChunkLoaded(p.x()>>4,p.z()>>4)){states[i]='0';return;}
        var block=world.getBlockAt(p.x(),p.y(),p.z());
        states[i]=(byte)(block.getType().isAir()?'2':block.getType()!=p.expected().getMaterial()?'3':block.getBlockData().matches(p.expected())?'1':'4');
    }
    private void scan(){
        long until=System.nanoTime()+scanNanos;int n=0;
        while(n++<budget&&System.nanoTime()<until){
            if(!dirty.isEmpty()){var it=dirty.iterator();int i=it.next();it.remove();check(i);}
            else{check(cursor);cursor=(cursor+1)%positions.size();}
        }
    }
    private void changed(org.bukkit.block.Block block){
        if(!block.getWorld().equals(world))return;
        for(int dx=-1;dx<=1;dx++)for(int dy=-1;dy<=1;dy++)for(int dz=-1;dz<=1;dz++){
            Integer i=indices.get(key(block.getX()+dx,block.getY()+dy,block.getZ()+dz));if(i!=null)dirty.add(i);
        }
    }
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void place(BlockPlaceEvent e){changed(e.getBlock());}
    @EventHandler(priority=EventPriority.MONITOR,ignoreCancelled=true) public void breakBlock(BlockBreakEvent e){changed(e.getBlock());}
    private void upload(){
        if(syncing.get()||!sending.compareAndSet(false,true))return;
        // No world name, player names or credentials are part of the JSON payload.
        long sampledAt=System.currentTimeMillis();
        String packed;
        try(var output=new ByteArrayOutputStream()){
            try(var gzip=new GZIPOutputStream(output)){gzip.write(states);}
            packed=Base64.getEncoder().encodeToString(output.toByteArray());
        }catch(IOException e){sending.set(false);getLogger().warning("Prüfstand konnte nicht komprimiert werden.");return;}
        String payload="{\"fingerprint\":\""+fingerprint+"\",\"sampledAt\":"+sampledAt+",\"statesGzip\":\""+packed+"\"}";
        var request=HttpRequest.newBuilder(URI.create(endpoint)).timeout(Duration.ofSeconds(12))
            .header("Authorization","Bearer "+token).header("Content-Type","application/json")
            .POST(HttpRequest.BodyPublishers.ofString(payload)).build();
        http.sendAsync(request,HttpResponse.BodyHandlers.discarding()).orTimeout(15,TimeUnit.SECONDS).whenComplete((response,error)->{
            String result=error!=null?"Netzwerkfehler (erneuter Versuch folgt)":response.statusCode()==200?"OK": uploadError(response.statusCode());
            // This field is only displayed; no Bukkit/world access on the network thread.
            lastUpload=result;sending.set(false);
            if(error==null&&response.statusCode()==409)syncPlan(false);
            if(error!=null||response.statusCode()!=200)getLogger().warning("Atlas-Übertragung: "+result);
        });
    }
    private String uploadError(int code){return switch(code){
        case 401 -> "HTTP 401: write-token stimmt nicht mit LIVE_BUILD_WRITE_TOKEN überein";
        case 403 -> "HTTP 403: Zugang zum Deployment gesperrt";
        case 404 -> "HTTP 404: Endpoint oder Website-Deployment prüfen";
        case 409 -> "HTTP 409: Bauplan abweichend oder älterer Prüfstand; automatischer Planabgleich";
        case 400 -> "HTTP 400: Prüfstand oder Serveruhr prüfen";
        case 503 -> "HTTP 503: Vercel-/Redis-Einrichtung oder Datenbank prüfen";
        default -> "HTTP "+code;
    };}
    private void installPlan(PlanData plan) throws IOException {
        // All Bukkit parsing, world limits and swapping happen on the main server thread.
        List<Position> replacement=new ArrayList<>();Map<String,Integer> newIndices=new HashMap<>();
        Map<String,BlockData> palette=new HashMap<>();byte[] next=new byte[plan.entries.size()];Arrays.fill(next,(byte)'0');
        for(var entry:plan.entries){
            int x=Math.addExact(entry.x(),ox),y=Math.addExact(entry.y(),oy),z=Math.addExact(entry.z(),oz);
            if(y<world.getMinHeight()||y>=world.getMaxHeight()||Math.abs((long)x)>30000000||Math.abs((long)z)>30000000)throw new IOException("Bauplan außerhalb der Weltgrenzen.");
            BlockData expected=palette.computeIfAbsent(entry.state(),Bukkit::createBlockData);
            Integer oldIndex=indices.get(key(x,y,z));
            if(oldIndex!=null&&states!=null&&positions.get(oldIndex).expected().getAsString(true).equals(expected.getAsString(true)))next[replacement.size()]=states[oldIndex];
            newIndices.put(key(x,y,z),replacement.size());replacement.add(new Position(x,y,z,expected));
        }
        positions.clear();positions.addAll(replacement);indices.clear();indices.putAll(newIndices);
        states=next;fingerprint=plan.fingerprint;revision=plan.revision;cursor=0;dirty.clear();
    }
    private void syncPlan(boolean force){
        if(!isEnabled()||!force&&System.currentTimeMillis()-lastSyncAttempt<30000||!syncing.compareAndSet(false,true))return;
        lastSyncAttempt=System.currentTimeMillis();syncStatus="Wird abgeglichen";
        String planEndpoint=endpoint.substring(0,endpoint.length()-"build-progress".length())+"build-plan";
        var request=HttpRequest.newBuilder(URI.create(planEndpoint)).timeout(Duration.ofSeconds(20))
            .header("Authorization","Bearer "+token).header("If-None-Match","\""+fingerprint+"\"").GET().build();
        http.sendAsync(request,info->new LimitedBody(2*1024*1024)).orTimeout(25,TimeUnit.SECONDS).whenCompleteAsync((response,error)->{
            if(error!=null){syncStatus="Netzwerkfehler beim Bauplanabgleich";syncing.set(false);return;}
            try{
                if(response.statusCode()==304){syncStatus="Bauplan aktuell";syncing.set(false);return;}
                if(response.statusCode()!=200){syncStatus="Planabgleich "+uploadError(response.statusCode());getLogger().warning(syncStatus);syncing.set(false);return;}
                if(!response.headers().firstValue("X-Blackthorn-Plan-Schema").orElse("").equals("1"))throw new IOException("Website-Bauplanformat wird nicht unterstützt; Plugin aktualisieren.");
                byte[] bytes=response.body();
                PlanData plan=PlanData.decode(bytes);
                if(!plan.fingerprint.equals(response.headers().firstValue("X-Blackthorn-Fingerprint").orElse(""))||!String.valueOf(plan.entries.size()).equals(response.headers().firstValue("X-Blackthorn-Positions").orElse("")))throw new IOException("Unvollständiger oder widersprüchlicher Website-Bauplan.");
                if(!isEnabled()){syncing.set(false);return;}
                Bukkit.getScheduler().runTask(this,()->{
                    try{
                        if(!fingerprint.equals(plan.fingerprint)){
                            installPlan(plan);lastUpload="Neuer Plan übernommen; nächste Übertragung folgt";
                            getLogger().info("Website-Bauplan "+revision+" übernommen: "+positions.size()+" Positionen, Plan "+fingerprint.substring(0,12));
                            network.execute(()->cachePlan(bytes));
                        }
                        syncStatus="Bauplan aktuell";
                    }catch(Exception e){syncStatus="Bauplan abgelehnt: "+e.getMessage();getLogger().warning(syncStatus+"; letzter gültiger Plan bleibt erhalten.");}
                    finally{syncing.set(false);}
                });
            }catch(Exception e){syncStatus="Planabgleich fehlgeschlagen: "+e.getMessage();getLogger().warning(syncStatus);syncing.set(false);}
        },network);
    }
    private void cachePlan(byte[] bytes){
        try{Path folder=getDataFolder().toPath();Files.createDirectories(folder);Path temp=folder.resolve("current-plan.tmp");Files.write(temp,bytes);
            Files.move(temp,folder.resolve("current-plan.tsv.gz"),StandardCopyOption.REPLACE_EXISTING);
        }catch(IOException e){getLogger().warning("Bauplan aktiv, konnte aber nicht lokal gespeichert werden.");}
    }
    @Override public boolean onCommand(CommandSender sender,Command command,String label,String[] args){
        if(!sender.hasPermission("blackthorn.live.admin")){sender.sendMessage("Keine Berechtigung.");return true;}
        if(args.length>0&&args[0].equalsIgnoreCase("rescan")){Arrays.fill(states,(byte)'0');cursor=0;dirty.clear();sender.sendMessage("Prüfung zurückgesetzt. Ungeladene Chunks bleiben ungeprüft.");}
        else if(args.length>0&&args[0].equalsIgnoreCase("sync")){syncPlan(true);sender.sendMessage("Bauplanabgleich angefordert. /blackthornlive status zeigt das Ergebnis.");}
        else sender.sendMessage("Blackthorn Live: "+positions.size()+" Positionen, Plan "+fingerprint.substring(0,12)+", Scan bei "+cursor+", Upload: "+lastUpload+", Abgleich: "+syncStatus);
        return true;
    }
    @Override public void onDisable(){if(http!=null)http.shutdownNow();if(network!=null)network.shutdownNow();}
}

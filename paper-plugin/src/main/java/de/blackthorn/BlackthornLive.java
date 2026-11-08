package de.blackthorn;

import java.io.*;
import java.net.URI;
import java.net.http.*;
import java.nio.charset.StandardCharsets;
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
    private String fingerprint, token, endpoint;
    private volatile String lastUpload="Noch keine Übertragung";
    private World world;
    private int cursor, budget, ox, oy, oz;
    private long scanNanos;
    private final AtomicBoolean sending = new AtomicBoolean();
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
            Map<String,BlockData> palette=new HashMap<>();
            try(var in=new BufferedReader(new InputStreamReader(new GZIPInputStream(Objects.requireNonNull(getResource("plan.tsv.gz"))),StandardCharsets.UTF_8))) {
                fingerprint=in.readLine().split("\t")[0];String line;
                while((line=in.readLine())!=null){String[] p=line.split("\t");
                    int x=Integer.parseInt(p[0])+ox,y=Integer.parseInt(p[1])+oy,z=Integer.parseInt(p[2])+oz;
                    if(y<world.getMinHeight()||y>=world.getMaxHeight())throw new IllegalArgumentException("Bauplan außerhalb der Welthöhe.");
                    indices.put(key(x,y,z),positions.size());
                    positions.add(new Position(x,y,z,palette.computeIfAbsent(p[3],Bukkit::createBlockData)));
                }
            }
            states=new byte[positions.size()];Arrays.fill(states,(byte)'0');
            network=Executors.newSingleThreadExecutor();
            http=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(8)).executor(network).followRedirects(HttpClient.Redirect.NEVER).build();
            Bukkit.getPluginManager().registerEvents(this,this);
            Bukkit.getScheduler().runTaskTimer(this,this::scan,1,1);
            long period=Math.max(5,getConfig().getInt("upload-seconds",10))*20L;
            Bukkit.getScheduler().runTaskTimer(this,this::upload,period,period);
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
        if(!sending.compareAndSet(false,true))return;
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
        http.sendAsync(request,HttpResponse.BodyHandlers.discarding()).whenComplete((response,error)->{
            String result=error!=null?"Netzwerkfehler (erneuter Versuch folgt)":response.statusCode()==200?"OK": "HTTP "+response.statusCode()+" (Token, Bauplan und Vercel-Konfiguration prüfen)";
            // This field is only displayed; no Bukkit/world access on the network thread.
            lastUpload=result;sending.set(false);
            if(error!=null||response.statusCode()!=200)getLogger().warning("Atlas-Übertragung: "+result);
        });
    }
    @Override public boolean onCommand(CommandSender sender,Command command,String label,String[] args){
        if(!sender.hasPermission("blackthorn.live.admin")){sender.sendMessage("Keine Berechtigung.");return true;}
        if(args.length>0&&args[0].equalsIgnoreCase("rescan")){Arrays.fill(states,(byte)'0');cursor=0;dirty.clear();sender.sendMessage("Prüfung zurückgesetzt. Ungeladene Chunks bleiben ungeprüft.");}
        else sender.sendMessage("Blackthorn Live: "+positions.size()+" Positionen, Scan bei "+cursor+", Upload: "+lastUpload);
        return true;
    }
    @Override public void onDisable(){if(network!=null)network.shutdownNow();}
}

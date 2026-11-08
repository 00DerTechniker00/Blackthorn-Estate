package de.blackthorn;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.regex.Pattern;
import java.util.zip.GZIPInputStream;

/** Pure data decoder: no Bukkit calls and no executable content in downloaded plans. */
final class PlanData {
    private static final Pattern STATE=Pattern.compile("[a-z0-9_.-]+:[a-z0-9_]+(?:\\[[a-z0-9_=,.-]+\\])?");
    record Entry(int x,int y,int z,String state) {}
    final String fingerprint, revision;
    final List<Entry> entries;
    private PlanData(String fingerprint,String revision,List<Entry> entries){this.fingerprint=fingerprint;this.revision=revision;this.entries=List.copyOf(entries);}
    static PlanData decode(byte[] gzip) throws IOException {
        if(gzip.length>2*1024*1024)throw new IOException("Bauplandatei zu groß.");
        byte[] bytes;
        try(var in=new GZIPInputStream(new ByteArrayInputStream(gzip))){bytes=in.readNBytes(32*1024*1024+1);}
        if(bytes.length>32*1024*1024)throw new IOException("Entpackter Bauplan zu groß.");
        try(var reader=new BufferedReader(new StringReader(new String(bytes,StandardCharsets.UTF_8)))){
            String header=reader.readLine();String[] info=header==null?new String[0]:header.split("\t",-1);
            if(info.length!=2||!info[0].matches("[a-f0-9]{64}")||!info[1].matches("[a-zA-Z0-9._-]{1,32}"))throw new IOException("Unbekanntes Bauplanformat.");
            List<Entry> entries=new ArrayList<>();Set<String> seen=new HashSet<>();String line;
            while((line=reader.readLine())!=null){
                String[] p=line.split("\t",-1);
                if(p.length!=4||entries.size()>=500000||!STATE.matcher(p[3]).matches())throw new IOException("Ungültige Bauplanzeile.");
                int x,y,z;
                try{x=Integer.parseInt(p[0]);y=Integer.parseInt(p[1]);z=Integer.parseInt(p[2]);}catch(NumberFormatException e){throw new IOException("Ungültige Koordinaten.");}
                if(Math.abs((long)x)>30000000||Math.abs((long)z)>30000000||!seen.add(x+","+y+","+z))throw new IOException("Doppelte oder unzulässige Koordinaten.");
                entries.add(new Entry(x,y,z,p[3]));
            }
            if(entries.isEmpty())throw new IOException("Leerer Bauplan.");
            return new PlanData(info[0],info[1],entries);
        }
    }
}

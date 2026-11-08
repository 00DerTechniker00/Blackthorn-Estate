package de.blackthorn;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.zip.GZIPOutputStream;
public final class PlanDataCheck {
 static byte[] zip(String text)throws Exception{var output=new ByteArrayOutputStream();try(var gzip=new GZIPOutputStream(output)){gzip.write(text.getBytes(StandardCharsets.UTF_8));}return output.toByteArray();}
 static void invalid(String text)throws Exception{try{PlanData.decode(zip(text));throw new AssertionError("Invalid plan accepted");}catch(IOException expected){}}
 public static void main(String[]args)throws Exception{
  var live=PlanData.decode(Files.readAllBytes(Path.of(args[0])));if(live.entries.size()<100000)throw new AssertionError("Current plan incomplete");
  String head="a".repeat(64)+"\t6.1\n",row="-700\t95\t790\tminecraft:stone\n";
  var plan=PlanData.decode(zip(head+row));if(!plan.revision.equals("6.1")||plan.entries.size()!=1)throw new AssertionError();
  invalid(head);invalid(head+row+row);invalid("wrong\t6.1\n"+row);invalid(head+"0\tx\t0\tminecraft:stone\n");invalid(head+"0\t95\t0\t<script>\n");
  try{PlanData.decode(new byte[]{1,2,3});throw new AssertionError();}catch(IOException expected){}
  var limited=new LimitedBody(3);boolean[] cancelled={false};limited.onSubscribe(new java.util.concurrent.Flow.Subscription(){public void request(long n){}public void cancel(){cancelled[0]=true;}});
  limited.onNext(java.util.List.of(java.nio.ByteBuffer.wrap(new byte[]{1,2,3,4})));
  if(!cancelled[0]||!limited.getBody().toCompletableFuture().isCompletedExceptionally())throw new AssertionError("Download limit failed");
  System.out.println("Plan decoder: real plan, revision change, invalid coordinates, duplicates and corrupt files checked.");
 }
}

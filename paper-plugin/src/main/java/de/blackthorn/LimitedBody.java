package de.blackthorn;
import java.io.*;
import java.net.http.HttpResponse;
import java.nio.ByteBuffer;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.Flow;
/** Caps plan downloads while streaming, before allocating an unbounded response body. */
final class LimitedBody implements HttpResponse.BodySubscriber<byte[]> {
 private final int limit;
 private final ByteArrayOutputStream output=new ByteArrayOutputStream();
 private final CompletableFuture<byte[]> result=new CompletableFuture<>();
 private Flow.Subscription subscription;
 LimitedBody(int limit){this.limit=limit;}
 public CompletionStage<byte[]> getBody(){return result;}
 public void onSubscribe(Flow.Subscription subscription){this.subscription=subscription;subscription.request(1);}
 public void onNext(List<ByteBuffer> buffers){
  for(var buffer:buffers){
   if(buffer.remaining()>limit-output.size()){subscription.cancel();result.completeExceptionally(new IOException("Bauplandownload zu groß."));return;}
   byte[] bytes=new byte[buffer.remaining()];buffer.get(bytes);output.writeBytes(bytes);
  }
  subscription.request(1);
 }
 public void onError(Throwable error){result.completeExceptionally(error);}
 public void onComplete(){result.complete(output.toByteArray());}
}

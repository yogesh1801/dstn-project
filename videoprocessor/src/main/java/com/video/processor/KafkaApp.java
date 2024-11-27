package com.video.processor;

import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.common.functions.MapFunction;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.Path;
import java.io.IOException;
import java.io.ByteArrayOutputStream;
import java.util.zip.Inflater;
import java.util.zip.DataFormatException;

public class KafkaApp {
    private static final Logger LOG = LoggerFactory.getLogger(KafkaApp.class);

    public static class SegmentWriter implements MapFunction<Tuple2<String, byte[]>, Tuple2<String, byte[]>> {
        private final String outputDir;
        private static final int BUFFER_SIZE = 4242880;
        
        public SegmentWriter(String outputDir) {
            this.outputDir = outputDir;
        }

        private byte[] decompress(byte[] data) throws IOException {
            Inflater inflater = new Inflater();
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream(data.length);
            try {
                inflater.setInput(data);
                byte[] buffer = new byte[BUFFER_SIZE];
                while (!inflater.finished()) {
                    int count = inflater.inflate(buffer);
                    outputStream.write(buffer, 0, count);
                }
                return outputStream.toByteArray();
            } catch (DataFormatException e) {
                throw new IOException("Error decompressing data", e);
            } finally {
                inflater.end();
                outputStream.close();
            }
        }

        @Override
        public Tuple2<String, byte[]> map(Tuple2<String, byte[]> tuple) throws Exception {
            String key = tuple.f0;
            byte[] compressedValue = tuple.f1;
            
            if (key != null && compressedValue != null && compressedValue.length > 0) {
                try {
                    byte[] decompressedValue = decompress(compressedValue);
                    String filename = String.format("%s/%s.ts", outputDir, key);
                    Path filePath = Paths.get(filename);
                    
                    Files.write(filePath, decompressedValue);
                    LOG.info("Wrote segment file: {}, Original size: {} bytes, Decompressed size: {} bytes", 
                            filename, compressedValue.length, decompressedValue.length);
                    
                } catch (IOException e) {
                    LOG.error("Error processing segment for key {}: {}", key, e.getMessage());
                    if (e.getCause() instanceof DataFormatException) {
                        LOG.error("Data format error - possibly not zlib compressed");
                    }
                    throw e;
                }
            } else {
                LOG.warn("Received invalid data - Key: {}, Value size: {}", 
                        key, 
                        compressedValue != null ? compressedValue.length : "null");
            }
            
            return tuple;
        }
    }

    public static void main(String[] args) throws Exception {
        LOG.info("Starting Kafka Application with Zlib decompression...");
        
        String outputDir = args.length > 0 ? args[0] : "1080p";
        String bootstrapServers = args.length > 1 ? args[1] : "192.168.1.114:9092";
        String topic = args.length > 2 ? args[2] : "raw-video-data";
        
        Files.createDirectories(Paths.get(outputDir));
        LOG.info("Using output directory: {}", outputDir);
        
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        KafkaSource<Tuple2<String, byte[]>> source = KafkaSource.<Tuple2<String, byte[]>>builder()
                .setBootstrapServers(bootstrapServers)
                .setTopics(topic)
                .setGroupId("video-processor-group")
                .setDeserializer(new CustomDeSerializer())
                .setStartingOffsets(OffsetsInitializer.latest())
                .build();

        env.fromSource(source, 
                      org.apache.flink.api.common.eventtime.WatermarkStrategy.noWatermarks(), 
                      "Kafka Source")
           .map(new SegmentWriter(outputDir))
           .name("Segment Writer");

        env.execute("Video Segment Processor");
    }
}
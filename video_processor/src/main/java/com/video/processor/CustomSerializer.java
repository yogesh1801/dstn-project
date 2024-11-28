package com.video.processor;

import org.apache.flink.streaming.connectors.kafka.KafkaSerializationSchema;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.nio.charset.StandardCharsets;
import org.apache.flink.api.java.tuple.Tuple2;

import javax.annotation.Nullable;


public class CustomSerializer implements KafkaSerializationSchema<Tuple2<String, byte[]>> {
    private String topic;

    public CustomSerializer(String topic) {
        this.topic = topic;
    }

    @Override
    public ProducerRecord<byte[], byte[]> serialize(
            Tuple2<String, byte[]> element, @Nullable Long timestamp) {
        byte[] key = element.f0 != null ? element.f0.getBytes(StandardCharsets.UTF_8) : null;
        return new ProducerRecord<>(topic, key, element.f1);
    }
}
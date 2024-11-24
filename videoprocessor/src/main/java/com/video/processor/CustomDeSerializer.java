package com.video.processor;

import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema;
import org.apache.flink.api.common.typeinfo.TypeHint;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.flink.util.Collector;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.apache.flink.api.java.tuple.Tuple2;

public class CustomDeSerializer implements KafkaRecordDeserializationSchema<Tuple2<String, byte[]>>{
    @Override
    public void deserialize(ConsumerRecord<byte[], byte[]> record, Collector<Tuple2<String, byte[]>> out) throws IOException {
        String key = record.key() != null ? new String(record.key(), StandardCharsets.UTF_8) : null;
        out.collect(new Tuple2<>(key, record.value()));
    }


    @Override
    public TypeInformation<Tuple2<String, byte[]>> getProducedType() {
        return TypeInformation.of(new TypeHint<Tuple2<String, byte[]>>() {});
    }
}

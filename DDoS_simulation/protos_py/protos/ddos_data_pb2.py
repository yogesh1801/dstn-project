# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: protos/ddos_data.proto
# Protobuf Python Version: 5.28.3
"""Generated protocol buffer code."""

from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC, 5, 28, 3, "", "protos/ddos_data.proto"
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b"\n\x16protos/ddos_data.proto\"\x84\x07\n\rNetworkRecord\x12\n\n\x02ID\x18\x01 \x01(\x05\x12\x0f\n\x07pkSeqID\x18\x02 \x01(\x05\x12\r\n\x05stime\x18\x03 \x01(\x01\x12\x0c\n\x04\x66lgs\x18\x04 \x01(\t\x12\x13\n\x0b\x66lgs_number\x18\x05 \x01(\x05\x12\r\n\x05proto\x18\x06 \x01(\t\x12\x14\n\x0cproto_number\x18\x07 \x01(\x05\x12\r\n\x05saddr\x18\x08 \x01(\t\x12\r\n\x05sport\x18\t \x01(\x05\x12\r\n\x05\x64\x61\x64\x64r\x18\n \x01(\t\x12\r\n\x05\x64port\x18\x0b \x01(\x05\x12\x0c\n\x04pkts\x18\x0c \x01(\x05\x12\r\n\x05\x62ytes\x18\r \x01(\x05\x12\r\n\x05state\x18\x0e \x01(\t\x12\x14\n\x0cstate_number\x18\x0f \x01(\x05\x12\r\n\x05ltime\x18\x10 \x01(\x01\x12\x0b\n\x03seq\x18\x11 \x01(\x05\x12\x0b\n\x03\x64ur\x18\x12 \x01(\x01\x12\x0c\n\x04mean\x18\x13 \x01(\x01\x12\x0e\n\x06stddev\x18\x14 \x01(\x01\x12\x0b\n\x03sum\x18\x15 \x01(\x01\x12\x0b\n\x03min\x18\x16 \x01(\x01\x12\x0b\n\x03max\x18\x17 \x01(\x01\x12\r\n\x05spkts\x18\x18 \x01(\x05\x12\r\n\x05\x64pkts\x18\x19 \x01(\x05\x12\x0e\n\x06sbytes\x18\x1a \x01(\x05\x12\x0e\n\x06\x64\x62ytes\x18\x1b \x01(\x05\x12\x0c\n\x04rate\x18\x1c \x01(\x01\x12\r\n\x05srate\x18\x1d \x01(\x01\x12\r\n\x05\x64rate\x18\x1e \x01(\x01\x12\x11\n\tTnBPSrcIP\x18\x1f \x01(\x05\x12\x11\n\tTnBPDstIP\x18  \x01(\x05\x12\x12\n\nTnP_PSrcIP\x18! \x01(\x05\x12\x12\n\nTnP_PDstIP\x18\" \x01(\x05\x12\x14\n\x0cTnP_PerProto\x18# \x01(\x05\x12\x15\n\rTnP_Per_Dport\x18$ \x01(\x05\x12\x1a\n\x12\x41R_P_Proto_P_SrcIP\x18% \x01(\x01\x12\x1a\n\x12\x41R_P_Proto_P_DstIP\x18& \x01(\x01\x12\x19\n\x11N_IN_Conn_P_DstIP\x18' \x01(\x05\x12\x19\n\x11N_IN_Conn_P_SrcIP\x18( \x01(\x05\x12\x1a\n\x12\x41R_P_Proto_P_Sport\x18) \x01(\x01\x12\x1a\n\x12\x41R_P_Proto_P_Dport\x18* \x01(\x01\x12(\n Pkts_P_State_P_Protocol_P_DestIP\x18+ \x01(\x01\x12'\n\x1fPkts_P_State_P_Protocol_P_SrcIP\x18, \x01(\x01\x12\x0e\n\x06\x61ttack\x18- \x01(\x05\x12\x10\n\x08\x63\x61tegory\x18. \x01(\t\x12\x13\n\x0bsubcategory\x18/ \x01(\tb\x06proto3"
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "protos.ddos_data_pb2", _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals["_NETWORKRECORD"]._serialized_start = 27
    _globals["_NETWORKRECORD"]._serialized_end = 927
# @@protoc_insertion_point(module_scope)

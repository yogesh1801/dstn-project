from protos_py.protos import ddos_data_pb2


def create_ddos_record_proto(row):
    network_record = ddos_data_pb2.NetworkRecord()
    network_record.ID = int(row["ID"])
    network_record.pkSeqID = int(row["pkSeqID"])
    network_record.stime = float(row["stime"])
    network_record.flgs = row["flgs"]
    network_record.flgs_number = int(row["flgs_number"])
    network_record.proto = row["proto"]
    network_record.proto_number = int(row["proto_number"])
    network_record.saddr = row["saddr"]
    network_record.sport = int(row["sport"])
    network_record.daddr = row["daddr"]
    network_record.dport = int(row["dport"])
    network_record.pkts = int(row["pkts"])
    network_record.bytes = int(row["bytes"])
    network_record.state = row["state"]
    network_record.state_number = int(row["state_number"])
    network_record.ltime = float(row["ltime"])
    network_record.seq = int(row["seq"])
    network_record.dur = float(row["dur"])
    network_record.mean = float(row["mean"])
    network_record.stddev = float(row["stddev"])
    network_record.sum = float(row["sum"])
    network_record.min = float(row["min"])
    network_record.max = float(row["max"])
    network_record.spkts = int(row["spkts"])
    network_record.dpkts = int(row["dpkts"])
    network_record.sbytes = int(row["sbytes"])
    network_record.dbytes = int(row["dbytes"])
    network_record.rate = float(row["rate"])
    network_record.srate = float(row["srate"])
    network_record.drate = float(row["drate"])
    network_record.TnBPSrcIP = int(row["TnBPSrcIP"])
    network_record.TnBPDstIP = int(row["TnBPDstIP"])
    network_record.TnP_PSrcIP = int(row["TnP_PSrcIP"])
    network_record.TnP_PDstIP = int(row["TnP_PDstIP"])
    network_record.TnP_PerProto = int(row["TnP_PerProto"])
    network_record.TnP_Per_Dport = int(row["TnP_Per_Dport"])
    network_record.AR_P_Proto_P_SrcIP = float(row["AR_P_Proto_P_SrcIP"])
    network_record.AR_P_Proto_P_DstIP = float(row["AR_P_Proto_P_DstIP"])
    network_record.N_IN_Conn_P_DstIP = int(row["N_IN_Conn_P_DstIP"])
    network_record.N_IN_Conn_P_SrcIP = int(row["N_IN_Conn_P_SrcIP"])
    network_record.AR_P_Proto_P_Sport = float(row["AR_P_Proto_P_Sport"])
    network_record.AR_P_Proto_P_Dport = float(row["AR_P_Proto_P_Dport"])
    network_record.Pkts_P_State_P_Protocol_P_DestIP = float(
        row["Pkts_P_State_P_Protocol_P_DestIP"]
    )
    network_record.Pkts_P_State_P_Protocol_P_SrcIP = float(
        row["Pkts_P_State_P_Protocol_P_SrcIP"]
    )
    network_record.attack = int(row["attack"])
    network_record.category = row["category"]
    network_record.subcategory = row["subcategory"]

    return network_record

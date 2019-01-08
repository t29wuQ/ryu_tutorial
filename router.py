#coding: utf-8
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ipv4
from ryu.lib.packet import arp
from ryu.lib.packet import icmp
from ryu.lib.packet.packet import Packet
from ryu.lib.packet.ethernet import ethernet
from ryu.lib.packet.arp import arp
from ryu.lib.packet.ipv4 import ipv4


class Router(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Router, self).__init__(*args, **kwargs)
        # initialize mac address table.
        self.arp_table = {}
        self.mac_to_port = {}

    #Features Replyを受け取ったときの処理
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch() #空のマッチ
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)] #パケット全体の出力先をコントローラに
        self.add_flow(datapath, 0, match, actions) #優先度0(すべてのパケット)

    #フローエントリー追加
    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)] #インストラクション
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst) #flow modクラスのインスタンスを生成
        datapath.send_msg(mod) #flow mod メッセージを送信

    #パケットを受信
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        in_port = msg.match['in_port']
        dpid = datapath.id #接続しているopenflowスイッチのID

        packet = Packet(msg.data)
        ether_frame = packet.get_protocol(ethernet)
        if ether_frame.ethertype == ether.ETH_TYPE_ARP:
            self.logger.info("received arp dst: %s src: %s ?: %s", ether_frame.dst, ether_frame.src, msg.match['eth_dst']);
            self.receive_arp(datapath, packet, in_port)
        elif ether_frame.ethertype == ether.ETH_TYPE_IP:
            self.logger.info("received ip ")

    #受信パケットがARPのとき
    def receive_arp(self, datapath, packet, in_port):
        arp_packet = packet.get_protocol(arp)

        if arp_packet.opcode == 1: #ARP Request
            self.logger.info("arp request ip src: %s ip dst: %s port: %s ", arp_packet.src_ip, arp_packet.dst_ip, in_port)
        #elif arp_packet.opcode == 2: #ARP Reply
    
    #受信パケットがIPパケットのとき
    def receive_ip(self, datapath, packet, ether_frame, in_port):
        ip_packet = packet.get_protocol(ipv4)

        # if ip_packet.proto == inet.IPROTO_ICMP:
        # else:
        

    def struct_ip_packet(self, datapath, ether_frame, ip_packet, in_port):
        e = ethernet()
    

    #パケットを指定ポートに送信
    def send_packet(self, datapath, packet, out_port):
        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath = datapath, 
            buffer_id = OFP_NO_BUFFER, 
            actions = actions,
            in_port = datapath.ofproto.OFPP_CONTROLLER,
            data = p.data
        )
        datapath.send_msg(out)
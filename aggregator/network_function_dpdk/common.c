#include "../aggregator.h"

int check_if_ipv4(struct rte_mbuf *mbuf) {
  if (mbuf == NULL) {
    rte_panic("NULL in check ipv4");
  }
  if (mbuf->data_len <
      sizeof(struct rte_ether_hdr) + sizeof(struct rte_ipv4_hdr)) {
    return 0;
  }

  struct rte_ether_hdr *eth = rte_pktmbuf_mtod(mbuf, struct rte_ether_hdr *);

  if (eth->ether_type != rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4)) {
    return 0;
  }

  struct rte_ipv4_hdr *ipv4 = rte_pktmbuf_mtod_offset(
      mbuf, struct rte_ipv4_hdr *, sizeof(struct rte_ether_hdr));

  if (ipv4->next_proto_id != IPPROTO_TCP &&
      ipv4->next_proto_id != IPPROTO_UDP) {
    return 0;
  }
  return 1;
}

void send_all(thread_context_t *ctx, struct rte_mbuf **tx_pkts,
              uint16_t nb_pkt) {
  int remain = nb_pkt;
  if (!remain) {
    return;
  }

  struct rte_mbuf **mp = tx_pkts;
  int ret = 0;
  do {
    ret = rte_eth_tx_burst(ctx->port_id, ctx->queue_id, mp, remain);
    mp += ret;
    remain -= ret;
  } while (remain > 0);
}
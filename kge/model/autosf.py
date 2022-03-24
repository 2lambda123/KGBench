import torch
from kge import Config, Dataset
from kge.model.kge_model import RelationalScorer, KgeModel
import numpy as np

class AutoSFScorer(RelationalScorer):
    def __init__(self, config: Config, dataset: Dataset, configuration_key=None):
        super().__init__(config, dataset, configuration_key)
        self.A = self.get_option("A")
        self.K = self.get_option("K")


    def score_emb(self, s_emb, p_emb, o_emb, combine: str):
        n = p_emb.size(0)

        s_emb_chunk = s_emb.chunk(self.K, dim=1)
        p_emb_chunk = p_emb.chunk(self.K, dim=1)
        o_emb_chunk = o_emb.chunk(self.K, dim=1)
        
        A_np = np.array(self.A)
        A_np_notzero = np.flatnonzero(A_np)

        if combine == "spo":
            score = torch.zeros(n).to(self.config.get("job.device"))
            for idx in A_np_notzero:
                ii = idx // self.K  # row: s
                jj = idx % self.K   # column: o
                A_ij = A_np[idx]
                score += np.sign(A_ij) * (s_emb_chunk[ii] * p_emb_chunk[abs(A_ij)-1] * o_emb_chunk[jj]).sum(dim=1)

        elif combine == "sp_":
            mult_part = torch.zeros(n, p_emb.size(1)).view(n, self.K, -1).to(self.config.get("job.device"))
            for idx in A_np_notzero:
                ii = idx // self.K  # row: s
                jj = idx % self.K   # column: o
                A_ij = A_np[idx]
                mult_part[:,jj] += np.sign(A_ij) * (s_emb_chunk[ii] * p_emb_chunk[abs(A_ij)-1])
            mult_part = mult_part.view(n, -1)
            score = mult_part.mm(o_emb.transpose(0,1))

        elif combine == "_po":
            mult_part = torch.zeros(n, p_emb.size(1)).view(n, self.K, -1).to(self.config.get("job.device"))
            for idx in A_np_notzero:
                ii = idx // self.K  # row: s
                jj = idx % self.K   # column: o
                A_ij = A_np[idx]
                mult_part[:,ii] += np.sign(A_ij) * (o_emb_chunk[jj] * p_emb_chunk[abs(A_ij)-1])
            mult_part = mult_part.view(n, -1)
            score = mult_part.mm(s_emb.transpose(0,1))

        elif combine == "s_o":
            n = s_emb.size(0)
            mult_part = torch.zeros(n, s_emb.size(1)).view(n, self.K, -1).to(self.config.get("job.device"))
            for idx in A_np_notzero:
                ii = idx // self.K  # row: s
                jj = idx % self.K   # column: o
                A_ij = A_np[idx]
                mult_part[:,abs(A_ij)-1] += np.sign(A_ij) * (s_emb_chunk[ii] * o_emb_chunk[jj])
            mult_part = mult_part.view(n, -1)
            score = mult_part.mm(p_emb.transpose(0,1))

        else:
            return super().score_emb(s_emb, p_emb, o_emb, combine)

        return score.view(n, -1)      


    def score_emb_sp_given_negs(self, s_emb: torch.Tensor , p_emb: torch.Tensor, o_emb: torch.Tensor):
        """ 
            s_emb: batch_size * dim
            p_emb: batch_size * dim
            o_emb: batch_size * negs * dim
         """
        # p_emb_re, p_emb_im = (t.contiguous() for t in p_emb.chunk(2, dim=1))
        # o_emb_re, o_emb_im = (t.contiguous() for t in o_emb.chunk(2, dim=2))

        n = p_emb.size(0)

        s_emb_chunk = s_emb.chunk(self.K, dim=-1)
        p_emb_chunk = p_emb.chunk(self.K, dim=-1)
        
        A_np = np.array(self.A)
        A_np_notzero = np.flatnonzero(A_np)


        mult_part = torch.zeros(n, p_emb.size(1)).view(n, self.K, -1).to(self.config.get("job.device"))
        for idx in A_np_notzero:
            ii = idx // self.K  # row: s
            jj = idx % self.K   # column: o
            A_ij = A_np[idx]
            mult_part[:,jj] += np.sign(A_ij) * (s_emb_chunk[ii] * p_emb_chunk[abs(A_ij)-1])
        mult_part = mult_part.view(n, -1)

        return (mult_part.unsqueeze(dim=2) * (o_emb.transpose(1,2))).sum(dim=1)


class AutoSF(KgeModel):
    def __init__(
        self,
        config: Config,
        dataset: Dataset,
        configuration_key=None,
        init_for_load_only=False,
    ):
        super().__init__(
            config=config,
            dataset=dataset,
            scorer=AutoSFScorer,
            configuration_key=configuration_key,
            init_for_load_only=init_for_load_only,
        )






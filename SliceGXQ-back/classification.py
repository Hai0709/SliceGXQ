import copy
import torch
import os
import hydra
from dataset import get_dataset
from warnings import simplefilter
from gnnNets import get_gnnNets_explain, get_gnnNets
torch.cuda.empty_cache()

class Slicedmodel:
    def __init__(self, config, device, total_num_hop, num_hop, logger, dataset, state_dict, explain):
        self.config = config
        self.device = device
        self.dataset = dataset
        self.explain = explain
        self.total_num_hop = total_num_hop
        self.num_hop = num_hop
        self.logger = logger
        self.state_dict = state_dict
        self.submodel = self.createsub()
        if self.explain:
            self.model = get_gnnNets_explain(config.datasets.num_node_features, config.datasets.num_classes,
                                             self.config.models)
        else:
            self.model = get_gnnNets(config.datasets.num_node_features, config.datasets.num_classes, self.config.models)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        self.model.to(self.device)

    def createsub(self):
        if self.logger:
            self.logger.info(f'test layer: {self.num_hop}')
        layer_config = copy.deepcopy(self.config.models)
        if self.num_hop >= 1:
            layer_config.param.gnn_latent_dim = layer_config.param.gnn_latent_dim[:self.num_hop]
        else:
            if self.logger:
                self.logger.info(f'layer out of range')
        if self.explain:
            submodel = get_gnnNets_explain(self.config.datasets.num_node_features, self.config.datasets.num_classes,
                                           layer_config)
        else:
            submodel = get_gnnNets(self.config.datasets.num_node_features, self.config.datasets.num_classes,
                                   layer_config)
        new_state_dict = copy.deepcopy(self.state_dict)
        for key in list(new_state_dict.keys()):
            key_parts = key.split('.')
            if len(key_parts) > 1 and key_parts[1].isdigit():
                layer_idx = int(key_parts[1])
                if layer_idx >= len(layer_config.param.gnn_latent_dim):
                    del new_state_dict[key]
        submodel.load_state_dict(new_state_dict)
        submodel.eval()
        submodel.to(self.device)
        return submodel

@hydra.main(version_base=None, config_path='config', config_name='config')
def main(config):
    config.models.param = config.models.param[config.datasets.dataset_name]
    dataset = get_dataset(config.datasets.dataset_root, config.datasets.dataset_name)
    if dataset.data.x is not None:
        dataset.data.x = dataset.data.x.float()
    dataset.data.y = dataset.data.y.squeeze().long()
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    dataset.data.to(device)
    layer_nums = len(config.models.param.gnn_latent_dim)
    state_dict = torch.load(os.path.join(config.models.gnn_savedir,
                                         config.datasets.dataset_name,
                                         f'{config.models.gnn_name}_'
                                         f'{len(config.models.param.gnn_latent_dim)}l_best.pth'))['net']
    test_indices = torch.where(dataset.data.test_mask)[0].tolist()
    for i in range(layer_nums - 1, -1, -1):
        modelslice = Slicedmodel(config=config, device=device, total_num_hop=len(config.models.param.gnn_latent_dim),
                                 num_hop=len(config.models.param.gnn_latent_dim) - i, logger=None,
                                 dataset=dataset,
                                 state_dict=state_dict, explain=False)
        prediction = modelslice.submodel(dataset.data).softmax(-1)

if __name__ == '__main__':
    import sys

    simplefilter(action="ignore", category=FutureWarning)
    sys.argv.append(f"models.gnn_savedir={os.path.join(os.path.dirname(__file__), 'checkpoints')}")
    main()

import logging
from pathlib import Path

import torch
import torchvision
import torchvision.transforms as transforms

from ada_verona.robustness_experiment_box.database.dataset.experiment_dataset import ExperimentDataset
from ada_verona.robustness_experiment_box.database.dataset.pytorch_experiment_dataset import PytorchExperimentDataset
from ada_verona.robustness_experiment_box.database.experiment_repository import ExperimentRepository
from ada_verona.robustness_experiment_box.dataset_sampler.dataset_sampler import DatasetSampler
from ada_verona.robustness_experiment_box.dataset_sampler.predictions_based_sampler import PredictionsBasedSampler
from ada_verona.robustness_experiment_box.epsilon_value_estimator.binary_search_epsilon_value_estimator import (
    BinarySearchEpsilonValueEstimator,
)
from ada_verona.robustness_experiment_box.epsilon_value_estimator.epsilon_value_estimator import EpsilonValueEstimator
from ada_verona.robustness_experiment_box.verification_module.attack_estimation_module import AttackEstimationModule
from ada_verona.robustness_experiment_box.verification_module.attacks.fgsm_attack import FGSMAttack
from ada_verona.robustness_experiment_box.verification_module.property_generator.one2any_property_generator import (
    One2AnyPropertyGenerator,
)
from ada_verona.robustness_experiment_box.verification_module.property_generator.one2one_property_generator import (
    One2OnePropertyGenerator,
)
from ada_verona.robustness_experiment_box.verification_module.property_generator.property_generator import (
    PropertyGenerator,
)

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
torch.manual_seed(0)

def create_distribution(
    experiment_repository: ExperimentRepository,
    dataset: ExperimentDataset,
    dataset_sampler: DatasetSampler,
    epsilon_value_estimator: EpsilonValueEstimator,
    property_generator: PropertyGenerator,
):
    network_list = experiment_repository.get_network_list()
    failed_networks = []
    for network in network_list:
        try:
            sampled_data = dataset_sampler.sample(network, dataset)
        except Exception as e:
            logging.info(f"failed for network: {network} with error: {e}")
            failed_networks.append(network)
            continue
        for data_point in sampled_data:
            verification_context = experiment_repository.create_verification_context(
                network, data_point, property_generator
            )

            epsilon_value_result = epsilon_value_estimator.compute_epsilon_value(verification_context)

            experiment_repository.save_result(epsilon_value_result)

    experiment_repository.save_plots()
    logging.info(f"Failed for networks: {failed_networks}")


def main():
    timeout = 600
    epsilon_list = [0.001, 0.005, 0.05, 0.08]
    experiment_repository_path = Path("../tests/test_experiment")
    network_folder = Path("../tests/test_experiment/data/networks")
    torch_dataset = torchvision.datasets.MNIST(
        root="./data", train=True, download=True, transform=transforms.ToTensor()
    )

    dataset = PytorchExperimentDataset(dataset=torch_dataset)

    experiment_repository = ExperimentRepository(base_path=experiment_repository_path, network_folder=network_folder)

    # Create distribution using one-to-one verification with FGSM attack
    experiment_name = "fgsm_one2one"
    property_generator = One2OnePropertyGenerator(target_class=1)

    verifier = AttackEstimationModule(attack=FGSMAttack())

    epsilon_value_estimator = BinarySearchEpsilonValueEstimator(
        epsilon_value_list=epsilon_list.copy(), verifier=verifier
    )
    dataset_sampler = PredictionsBasedSampler(sample_correct_predictions=True)
    experiment_repository.initialize_new_experiment(experiment_name)
    experiment_repository.save_configuration(
        dict(
            experiment_name=experiment_name,
            experiment_repository_path=str(experiment_repository_path),
            network_folder=str(network_folder),
            dataset=str(dataset),
            timeout=timeout,
            epsilon_list=[str(x) for x in epsilon_list],
        )
    )
    create_distribution(experiment_repository, dataset, dataset_sampler, epsilon_value_estimator, property_generator)

    # Create distribution using FGSM attack with one-to-any property generator
    experiment_name = "fgsm_one2any"
    property_generator = One2AnyPropertyGenerator()
    verifier = AttackEstimationModule(attack=FGSMAttack())
    epsilon_value_estimator = BinarySearchEpsilonValueEstimator(
        epsilon_value_list=epsilon_list.copy(), verifier=verifier
    )
    dataset_sampler = PredictionsBasedSampler(sample_correct_predictions=True)
    experiment_repository.initialize_new_experiment(experiment_name)
    experiment_repository.save_configuration(
        dict(
            experiment_name=experiment_name,
            experiment_repository_path=str(experiment_repository_path),
            network_folder=str(network_folder),
            dataset=str(dataset),
            timeout=timeout,
            epsilon_list=[str(x) for x in epsilon_list],
        )
    )

    create_distribution(experiment_repository, dataset, dataset_sampler, epsilon_value_estimator, property_generator)


if __name__ == "__main__":
    main()

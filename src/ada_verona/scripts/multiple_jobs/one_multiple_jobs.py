import argparse
import logging
from pathlib import Path

from ada_verona.robustness_experiment_box.database.experiment_repository import ExperimentRepository
from ada_verona.robustness_experiment_box.epsilon_value_estimator.binary_search_epsilon_value_estimator import (
    BinarySearchEpsilonValueEstimator,
)
from ada_verona.robustness_experiment_box.verification_module.attack_estimation_module import AttackEstimationModule
from ada_verona.robustness_experiment_box.verification_module.attacks.pgd_attack import PGDAttack

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

if __name__ == "__main__":
    # parse arguments from batch script.
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_verification_context", type=Path)
    parser.add_argument("--base_path_experiment_repository")
    parser.add_argument("--network_folder")
    parser.add_argument("--experiment_name")
    parser.add_argument("--epsilon_list", type=float, nargs="+")
    args = parser.parse_args()

    # reload experiment repository
    baby_experiment_repository = ExperimentRepository(
        base_path=Path(args.base_path_experiment_repository), network_folder=Path(args.network_folder)
    )
    baby_experiment_repository.load_experiment(experiment_name=args.experiment_name)

    # load autoverify module for verification (example)
    #verifier = GenericVerifierModule(verifier=MyExternalToolVerifier(), timeout=360)
    verifier = AttackEstimationModule(attack=PGDAttack(number_iterations=10, step_size=0.01)) 
    eps_list = args.epsilon_list

    # create the binary search module
    epsilon_value_estimator = BinarySearchEpsilonValueEstimator(epsilon_value_list=eps_list.copy(), verifier=verifier)

    # This is the same verification context as in the main file and
    # its loaded from the yaml file we created in the main file
    verification_context = baby_experiment_repository.load_verification_context_from_yaml(
        Path(args.file_verification_context)
    )

    # get the epsilon value and save it in the reloaded repository at the correct place
    epsilon_value_result = epsilon_value_estimator.compute_epsilon_value(verification_context)
    baby_experiment_repository.save_result(epsilon_value_result)

#!/usr/bin/env python3
"""
ADA-VERONA Plugin System Demo

This script demonstrates the plugin architecture that enables
ada-verona to work independently while optionally integrating with auto-verify.
"""


def demo_plugin_detection():
    """Demonstrate the plugin detection system."""
    print("ADA-VERONA Plugin System Demo")
    print("=" * 60)
    
    try:
        import ada_verona
        print("ada-verona imported successfully")
        
        # Check auto-verify availability
        print("\nSystem Status:")
        print(f"  • Auto-verify available: {ada_verona.HAS_AUTO_VERIFY}")
        print(f"  • PyAutoAttack available: {ada_verona.HAS_AUTOATTACK}")
        
        if ada_verona.HAS_AUTO_VERIFY:
            print("\nAuto-verify Integration:")
            print(f"  • Available verifiers: {ada_verona.AUTO_VERIFY_VERIFIERS}")
            
            # Demonstrate verifier creation
            if ada_verona.AUTO_VERIFY_VERIFIERS:
                print("\nTesting Verifier Creation:")
                for verifier_name in ada_verona.AUTO_VERIFY_VERIFIERS[:2]:  # Test first 2
                    try:
                        verifier = ada_verona.create_auto_verify_verifier(
                            verifier_name, timeout=60
                        )
                        if verifier:
                            print(f"  + {verifier_name}: {verifier.name}")
                        else:
                            print(f"  - {verifier_name}: Failed to create")
                    except Exception as e:
                        print(f"  ! {verifier_name}: {e}")
            
            print("\nUsage Examples:")
            print("  # Create formal verifier")
            print("  verifier = ada_verona.create_auto_verify_verifier('nnenum', timeout=300)")
            print("  ")
            print("  # Use in epsilon estimator")
            print("  from ada_verona.robustness_experiment_box.epsilon_value_estimator.")
            print("  from ada_verona.robustness_experiment_box.epsilon_value_estimator.")
            print("  from binary_search_epsilon_value_estimator import BinarySearchEpsilonValueEstimator")
            print("  estimator = BinarySearchEpsilonValueEstimator([0.01, 0.05], verifier)")
        
        else:
            print("\nAuto-verify not detected")
            print("  • Only attack-based verification available")
            print("  • Install auto-verify to enable formal verification")
            print("  • Example: pip install auto-verify")
        
        # Show attack-based verification (always available)
        print("\nAttack-based Verification (Always Available):")
        try:
            from ada_verona.robustness_experiment_box.verification_module.attack_estimation_module import (
                AttackEstimationModule,
            )
            from ada_verona.robustness_experiment_box.verification_module.attacks.pgd_attack import PGDAttack
            
            attack_verifier = AttackEstimationModule(
                attack=PGDAttack(number_iterations=10, step_size=0.01)
            )
            print(f"  + PGD Attack: {attack_verifier.name}")
            
            if ada_verona.HAS_AUTOATTACK:
                from ada_verona.robustness_experiment_box.verification_module.attacks.auto_attack_wrapper import (
                    AutoAttackWrapper,
                )
                auto_attack_verifier = AttackEstimationModule(
                    attack=AutoAttackWrapper()
                )
                print(f"  + Auto Attack: {auto_attack_verifier.name}")
        
        except ImportError as e:
            print(f"  - Error importing attack modules: {e}")
        
    except ImportError as e:
        print(f"Failed to import ada-verona: {e}")
        print("Please install ada-verona first: pip install ada-verona")
        return False
    
    return True


def demo_configuration():
    """Demonstrate the configuration system."""
    print("\nConfiguration System Demo")
    print("=" * 40)
    
    try:
        # Try to show auto-verify config if available
        import subprocess
        result = subprocess.run(
            ["auto-verify", "config", "show"], 
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            print("Current Auto-verify Configuration:")
            print(result.stdout)
        else:
            print("Auto-verify CLI not available")
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        print("Auto-verify CLI not found")
        
    print("\nConfiguration Commands:")
    print("  auto-verify config show              # Show current config")
    print("  auto-verify config set-env venv      # Use Python venv + uv")
    print("  auto-verify config set-env conda     # Use conda (traditional)")
    print("  auto-verify config set-env auto      # Auto-detect best option")
    print("  auto-verify config example           # Create example config file")


def demo_environment_strategies():
    """Demonstrate environment management strategies."""
    print("\nEnvironment Management Strategies")
    print("=" * 45)
    
    # Check for uv
    try:
        import subprocess
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, timeout=5)
        uv_available = result.returncode == 0
        if uv_available:
            print(f"uv available: {result.stdout.strip()}")
        else:
            print("uv not available")
    except (subprocess.SubprocessError, FileNotFoundError, ImportError):
        uv_available = False
        print("uv not available")
    
    # Check for conda
    try:
        import subprocess
        result = subprocess.run(["conda", "--version"], capture_output=True, text=True, timeout=5)
        conda_available = result.returncode == 0
        if conda_available:
            print(f"conda available: {result.stdout.strip()}")
        else:
            print("conda not available")
    except (subprocess.SubprocessError, FileNotFoundError, ImportError):
        conda_available = False
        print("conda not available")
    
    print("\nRecommendations:")
    if uv_available:
        print("  Recommended: Use 'venv' strategy (uv detected)")
        print("     - Faster installation")
        print("     - Simpler path management")
        print("     - Modern Python tooling")
    elif conda_available:
        print("  Recommended: Use 'conda' strategy (conda detected)")
        print("     - Better for complex dependencies")
        print("     - Proven stability")
    else:
        print("  Neither uv nor conda detected")
        print("     - Install uv: pip install uv")
        print("     - Or install conda/miniconda")


def demo_integration_examples():
    """Show integration examples."""
    print("\nIntegration Examples")
    print("=" * 30)
    
    print("""
Automatic Fallback Pattern:
```python
import ada_verona

# Auto-detect best available verifier
if ada_verona.HAS_AUTO_VERIFY and "nnenum" in ada_verona.AUTO_VERIFY_VERIFIERS:
    verifier = ada_verona.create_auto_verify_verifier("nnenum", timeout=300)
    print("Using formal verification")
else:
    from ada_verona.robustness_experiment_box.verification_module.attack_estimation_module import AttackEstimationModule
    from ada_verona.robustness_experiment_box.verification_module.attacks.pgd_attack import PGDAttack
    verifier = AttackEstimationModule(attack=PGDAttack(number_iterations=10, step_size=0.01))
    print("Using attack-based verification")
```

Direct Usage:
```python
import ada_verona

# List available verifiers
print(f"Available verifiers: {ada_verona.AUTO_VERIFY_VERIFIERS}")

# Create specific verifier
nnenum_verifier = ada_verona.create_auto_verify_verifier("nnenum", timeout=600)
abcrown_verifier = ada_verona.create_auto_verify_verifier("abcrown", timeout=300)
```

Advanced Configuration:
```python
# Create verifier with specific options
verifier = ada_verona.create_auto_verify_verifier(
    verifier_name="abcrown",
    timeout=600,
    config=Path("custom_config.yaml"),
    batch_size=128,
    cpu_gpu_allocation=(4, 1, 0)  # 4 CPUs, 1 GPU, GPU #0
)
```
""")


def main():
    """Main demo function."""
    print("Starting ADA-VERONA Plugin System Demo...\n")
    
    # Run demos
    success = demo_plugin_detection()
    if success:
        demo_configuration()
        demo_environment_strategies() 
        demo_integration_examples()
        
        print("\nDemo Complete!")
        print("Next Steps:")
        print("  1. Try the example script: python src/ada_verona/scripts/create_robustness_dist_with_auto_verify.py")
        print("  2. Read the documentation: PLUGIN_ARCHITECTURE.md")
        print("  3. Configure your environment: auto-verify config set-env auto")
    else:
        print("\nDemo failed - please install ada-verona first")
        print("   pip install ada-verona")


if __name__ == "__main__":
    main() 
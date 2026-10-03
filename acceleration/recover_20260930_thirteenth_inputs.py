"""Recover new thirteenth inputs with the frozen prior package checker."""
import recover_20260930_twelfth_inputs as prior

prior.MANIFESTS = {
    prior.B+'prism_first_choice_normalization/artifact_packages.json':
        'ce2eb961406cbd780f7ff93d81a1916484fd42f29a0ac43f17065f4988c5a9f9',
}

if __name__ == '__main__':
    prior.main()

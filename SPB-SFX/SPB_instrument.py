from SimEx.Calculators.GaussianPhotonSource import GaussianPhotonSource
from SimEx.Parameters.GaussWavefrontParameters import GaussWavefrontParameters

from prop import exfel_spb_kb_beamline
from SimEx.Parameters.WavePropagatorParameters import WavePropagatorParameters
from SimEx.Calculators.WavePropagator import WavePropagator

from SimEx.Calculators.XMDYNDemoPhotonMatterInteractor import XMDYNDemoPhotonMatterInteractor

from SimEx.Parameters.DetectorGeometry import DetectorPanel, DetectorGeometry
from SimEx.Parameters.SingFELPhotonDiffractorParameters import SingFELPhotonDiffractorParameters
from SimEx.Calculators.SingFELPhotonDiffractor import SingFELPhotonDiffractor

from SimEx.Utilities.Units import electronvolt, meter, joule, radian


# Photon source
wavefront_parameters = GaussWavefrontParameters(photon_energy=8.0e3*electronvolt,
                                                photon_energy_relative_bandwidth=1e-3,
                                                beam_diameter_fwhm=1.0e-4*meter,
                                                pulse_energy=2.0e-6*joule,
                                                number_of_transverse_grid_points=400,
                                                number_of_time_slices=30,
                                                z = 1*meter
                                                )
photon_source = GaussianPhotonSource(wavefront_parameters, input_path="/dev/null", output_path="initial_wavefront.h5")
photon_source.backengine()
photon_source.saveH5()

# Beam propagation
propagation_parameters = WavePropagatorParameters(beamline=exfel_spb_kb_beamline)
print(exfel_spb_kb_beamline.get_beamline())
# SPB_beamline = imp.load_source('SPB_beamline', '/gpfs/exfel/data/user/juncheng/SimEx-notebooks/SPB-SFX/SPB_beamline.py')
# propagation_parameters = WavePropagatorParameters(beamline=SPB_beamline)
propagator = WavePropagator(parameters=propagation_parameters,
                            input_path='initial_wavefront.h5',
                            output_path='prop_out.h5')
propagator.backengine()


# Photon-matter interaction
pmi_parameters={"number_of_trajectories" : 1,
                "random_rotation" : False}
photon_matter_interactor=XMDYNDemoPhotonMatterInteractor(parameters=pmi_parameters,
                                                         input_path='prop_out.h5',
                                                         output_path='pmi',
                                                         sample_path='5udc.pdb')

photon_matter_interactor.backengine()
photon_matter_interactor.saveH5()

# Detector
panel = DetectorPanel(ranges={"fast_scan_min" : 0, "fast_scan_max" : 100,
                              "slow_scan_min" : 0, "slow_scan_max" : 100},
                      pixel_size=6*220.0e-6*meter,
                      energy_response=1.0/electronvolt,
                      distance_from_interaction_plane=0.13*meter,
                      corners={"x" : -49, "y": -49},
                      saturation_adu=1.e6,
                      )
detector_geometry = DetectorGeometry(panels=panel,)
diffraction_parameters = SingFELPhotonDiffractorParameters(
                                               uniform_rotation=False,
                                               slice_interval=100,
                                               number_of_slices=100,
                                               number_of_diffraction_patterns=1,
                                               detector_geometry=detector_geometry,
                                              )

diffractor = SingFELPhotonDiffractor(parameters=diffraction_parameters,
                                     input_path='pmi',
                                     output_path="diffr")
diffractor.backengine()
diffractor.saveH5()

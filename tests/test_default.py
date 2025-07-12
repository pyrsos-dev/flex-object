import numpy as np
from src.extents import calculate_position, intersect, Sphere, Ray, get_ray_dir
from skyfield.api import EarthSatellite, load


def test_intersect():
    # Test basic sphere-ray intersection
    sphere = Sphere(center=np.array([0, 0, 0]), radius=1)
    ray = Ray(origin=np.array([0, 0, 2]), direction=np.array([0, 0, 1]))
    result = intersect(ray, sphere)
    assert result is not None

    # Test no intersection
    sphere = Sphere(center=np.array([0, 0, 0]), radius=1)
    ray = Ray(origin=np.array([0, 0, 2]), direction=np.array([1, 0, 0]))
    result = intersect(ray, sphere)
    assert result is None or len(result) == 0


def test_ray_dir():
    result = get_ray_dir(np.array([1, 0, 0]), np.array([0, 0, 1]), 0.0)
    assert np.allclose(result, np.array([1, 0, 0]))

    result = get_ray_dir(np.array([0, 0, 1]), np.array([1, 0, 0]), 0.0)
    assert np.allclose(result, np.array([0, 0, 1]))

    result = get_ray_dir(np.array([0, 0, 1]), np.array([0, 1, 0]), 0.0)
    assert np.allclose(result, np.array([0, 0, 1]))

    result = get_ray_dir(np.array([0, 0, 1]), np.array([0, 1, 0]), 90.0)
    assert np.allclose(result, np.array([-1, 0, 0]))


def test_calculate_position():
    ts = load.timescale()
    line1 = "1 63353U 25061C   25189.46845649  .00003010  00000+0  18746-3 0  9997"
    line2 = "2 63353  97.5272 164.2890 0021021   4.9701 355.1733 15.10164077 15668"
    satellite = EarthSatellite(line1, line2, "FOREST-6", ts)
    lat, lon = calculate_position(satellite, ts.utc(2025, 7, 9, 14, 30, 26), 0.0)
    assert abs(lat - 51.939250010509994) < 1e-1
    assert abs(lon - 10.351672865795695) < 1e-1

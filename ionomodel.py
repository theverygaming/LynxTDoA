import abc
import numpy as np
import tools


class PropModel(abc.ABC):
    @abc.abstractmethod
    def hop_distance(self, lata, lona, latb, lonb):
        pass


class SuperSimplePropModel(PropModel):
    def __init__(self, virtual_height: float, min_takeoff: float):
        """
        virtual_height: virtual height in kilometers (e.g. 400)
        min_takeoff: minimum takeoff angle in degrees (e.g. 10)
        """
        self._virtual_height = virtual_height * 1000
        min_takeoff_rad = np.radians(min_takeoff)
        self._max_1hop_ground_dist = (
            2
            * (
                np.acos(
                    (tools.EARTH_RADIUS_M * np.cos(min_takeoff_rad)) / (tools.EARTH_RADIUS_M + self._virtual_height)
                ) - min_takeoff_rad
            ) * tools.EARTH_RADIUS_M
        )

    def _half_hop(self, half_hop_ground_dist):
        # we need to know the angle at the center of earth for our triangle from the center
        # of earth, to the ionosphere (reflection point), and then to the transmitter/receiver
        # we can use the arc length of a circle for that
        # angle theta (radians) = length / radius
        center_angle = half_hop_ground_dist / tools.EARTH_RADIUS_M

        # law of cosines: we know angle alpha (earth center), longest side c (earth radius + ionosphere height)
        # and side b (earth radius) and want to know side a (radio path from source up to ionosphere)
        alpha = center_angle
        b = tools.EARTH_RADIUS_M
        c = tools.EARTH_RADIUS_M + self._virtual_height
        path_len = np.sqrt(b ** 2 + c ** 2 - 2 * b * c * np.cos(alpha))

        return path_len

    def hop_distance(self, lata, lona, latb, lonb):
        ground_dist = tools.haversine(lata, lona, latb, lonb)
        n_hops = np.ceil(ground_dist / self._max_1hop_ground_dist)

        half_hop_ground_dist = ground_dist / 2 / n_hops
        half_hop_path_dist = self._half_hop(half_hop_ground_dist)

        full_path_dist = half_hop_path_dist * 2 * n_hops

        return full_path_dist


# TODO: prop model with height profile

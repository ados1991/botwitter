import collections.abc

from collections import namedtuple
from math import sqrt
from pathlib import Path

from PIL import Image as Image

from .logger import Logger


__all__ = (
    'RegionPosition',
    'RegionSize',
    'Region',
    'RegionLoader',
)


logger = Logger(__name__)


RegionPosition = namedtuple('RegionPosition', 'x y')

RegionSize = namedtuple('RegionSize', 'width height')


class Region(collections.abc.Hashable):
    """
    A `region` is an image associated to a given position.
    """

    __slots__ = (
        '_filepath',
        '_position',
        '_image',
    )

    def __init__(self, filepath, position):
        self._filepath = Path(filepath)
        logger.debug("Load region from file {!r}", str(self._filepath))
        self._position = RegionPosition(*position)
        self._image = Image.open(str(self._filepath))

    @property
    def filepath(self):
        return self._filepath

    @property
    def position(self):
        return self._position

    @property
    def size(self):
        return RegionSize(*self._image.size)

    def __repr__(self):
        return 'Region({0!r}, ({1.x!r}, {1.y!r}))'.format(
            str(self.filepath), self.position)

    def _histogram(self):
        return self._image.histogram()

    def rms(self, other):
        if not isinstance(other, Region):
            raise TypeError("other must be a Region instance")
        if self.position != other.position:
            raise ValueError("regions must have the same position")
        if self.size != other.size:
            raise ValueError("regions must have the same size")
        num_pixels = len(self._histogram())
        sum_sq_diff = sum(map(lambda a, b: (a - b)**2,
                              self._histogram(), other._histogram()))
        rms = sqrt(sum_sq_diff / num_pixels)
        logger.debug("RMS of {!r} and {!r} is {!r}", self, other, rms)
        return rms

    def similar(self, other, maxrms=None):
        if maxrms is None:
            return self == other
        rms = self.rms(other)
        if rms <= maxrms:
            logger.debug("{!r} and {!r} are similar, RMS <= {}",
                         self, other, maxrms)
            return True
        else:
            logger.debug("{!r} and {!r} are not similar, RMS > {}",
                         self, other, maxrms)
            return False

    def __eq__(self, other):
        if not isinstance(other, Region):
            return NotImplemented
        return (self.position == other.position and self.size == other.size and
                self._histogram() == other._histogram())

    def __hash__(self):
        return hash((self.position, self.size, self._histogram()))


class RegionLoader:

    def __init__(self, directory, suffix='.png'):
        self._directory = Path(directory)
        self._suffix = suffix

    @property
    def directory(self):
        return self._directory

    @property
    def suffix(self):
        return self._suffix

    def __repr__(self):
        return '{}({!r}, suffix={!r})'.format(
            str(self.directory), self.prefix, self.suffix)

    def getregions(self):
        # FIXME current implementation is greedy, all regions are loaded at
        # initialization
        region_dict = {}
        for path in self.directory.iterdir():
            if path.is_dir():
                dir_loader = RegionLoader(path, self.suffix)
                region_dict[path.name] = dir_loader.getregions()
            else:
                if len(path.suffixes) != 3 or path.suffix != self.suffix:
                    raise ValueError("incorrect region name: {!r}", str(path))
                position = RegionPosition(x=int(path.suffixes[0][1:]),
                                          y=int(path.suffixes[1][1:]))
                region = Region(path, position)
                name = path.name.split('.')[0]
                logger.debug("Found region {!r} in directory {!r}",
                             name, str(self.directory))
                region_dict[name] = region
        regions = type('regions', (object,), region_dict)
        return regions

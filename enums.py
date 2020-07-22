import enum


class Genres(enum.Enum):
    alternative = 'Alternative'
    blues = 'Blues'
    classical = 'Classical'
    country = 'Country'           
    electronic = 'Electronic'
    folk = 'Folk'
    funk = 'Funk'
    hipHop = 'Hip-Hop'
    metal = 'Heavy Metal'
    instrumental = 'Instrumental'
    jazz = 'Jazz'
    theatre = 'Musical Theatre'
    pop = 'Pop'
    punk = 'Punk'
    RB = 'R&B'
    reggae = 'Reggae'
    rock = 'Rock n Roll'
    soul = 'Soul'
    other = 'Other'

    @classmethod
    def choices(cls):
        return [(choice.name , choice.value) for choice in cls]


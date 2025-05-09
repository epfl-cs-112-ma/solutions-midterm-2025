# Rappel : sur papier, les `import` ne sont pas requis.
# De plus, toutes les `def __init__` qui sont marquées avec "init standard"
# n'ont pas besoin d'être écrites sur papier ; la mention "... # init standard"
# suffit.

# N'oubliez pas aussi qu'il y a beaucoup de solutions possibles. Cette
# version-ci n'est pas forcément meilleure q'une autre.

from __future__ import annotations

from abc import abstractmethod
from enum import Enum, auto
from typing import Final, Sequence


## Question 1. (2 points) -----------------------------------------------------

class ResourceKind(Enum):
    WOOD = auto()
    CARROT = auto()
    FISH = auto()
    MUSHROOM = auto()
    GOLD = auto()

# Alternative, puisqu'on n'utilise pas les propriétés particulières de chaque
# type de ressource, mais il fallait bien faire attention au Final.

class ResourceKind_Alt:
    name: Final[str]

    ... # init standard
    def __init__(self, name: str) -> None:
        self.name = name


## Question 2. (4 points) -----------------------------------------------------

## Pour Question 7
class Provider:
    # Ces 3 méthodes pourraient aussi être des @property

    def resources(self) -> frozenset[ResourceKind]:
        """Resources produced by this building, excluding market resources."""
        return frozenset()

    def is_market(self) -> bool:
        """Returns True if and only if this building is a market"""
        return False

    # Pour Question 9 (et éventuellement 4)
    def tower_count(self) -> int:
        """Number of towers in this building (0 for non-cities)."""
        return 0

class Building(Provider): # Provider pour Question 7
    pass

    # Pour Question 3 -- plus tard déplacée dans Provider pour Question 7
    # Alternative valable : méthodes abstraites avec implémentation répétée
    # dans les sous-classes. Pas de pénalité pour la duplication car elle est
    # "triviale" (résultat constant) et est compensée par le fait que les
    # méthodes sont abstraites.

    def resources(self) -> frozenset[ResourceKind]:
        """Resources produced by this building, excluding market resources."""
        return frozenset()

    def is_market(self) -> bool:
        """Returns True if and only if this building is a market"""
        return False

    # Pour Question 4 -- plus tard déplacée dans Provider pour Question 9
    # Même alternative
    def tower_count(self) -> int:
        """Number of towers in this building (0 for non-cities)."""
        return 0

class Factory(Building):
    resource: Final[ResourceKind]

    ... # init standard
    def __init__(self, resource: ResourceKind):
        super().__init__()
        self.resource = resource

    # Pour Question 3
    # overrides Building.resources
    def resources(self) -> frozenset[ResourceKind]:
        return frozenset({self.resource})

class City(Building):
    towers: Final[int]

    ... # init standard
    def __init__(self, towers: int):
        super().__init__()

        # bonus: vérification expresse de la validité du nombre de tours
        assert towers >= 1 and towers <= 3, f"nombre de tours invalide: {towers}"

        self.towers = towers

    # Pour Question 4
    # overrides Building.tower_count
    def tower_count(self) -> int:
        return self.towers

class Market(Building):
    pass

    # Pour Question 3
    # overrides Building.is_market
    def is_market(self) -> bool:
        return True


## Question 3. (5 points) -----------------------------------------------------

# Pour les marchés, nous avons besoin de savoir combien de ressources
# *possibles* existent.
MAX_RESOURCE_COUNT = 5 # ou len(ResourceKind) si on utilise un Enum

def count_building_resources(buildings: list[Building]) -> int:
    # On voulait un set ici pour dédupliquer les ressources en restant Θ(n)
    # où n = len(buildings). Avec une list, cela devenait Θ(n²) sans raison
    # valable.
    resources: set[ResourceKind] = set()

    for building in buildings:
        resources |= building.resources()
    resource_count_without_markets = len(resources)

    market_count = len([building.is_market() for building in buildings])
    # Alternative correcte :
    market_count = len([isinstance(building, Market) for building in buildings])

    return min(resource_count_without_markets + market_count, MAX_RESOURCE_COUNT)

# Alternative avec des match; acceptable mais 1 point de moins parce qu'on
# ne peut pas garantir l'exhaustivité ici.
# Aussi, on fuse le calcul des resources et des nombres de marchés.
#
# Cette alternative ne se généralise pas aussi bien à la gestion des cases,
# mais nous ne pénalisons pas cela dans la question 3.
def count_building_resources_with_match(buildings: list[Building]) -> int:
    resources: set[ResourceKind] = set()
    market_count = 0

    for building in buildings:
        match building:
            case Factory(): resources.add(building.resource)
            case Market(): market_count += 1
            case City(): pass

    resource_count_without_markets = len(resources)
    return min(resource_count_without_markets + market_count, MAX_RESOURCE_COUNT)


## Question 4. (4 points) -----------------------------------------------------

# peut aussi être "inlinée" dans count_building_points
def count_building_towers(buildings: list[Building]) -> int:
    return sum([building.tower_count() for building in buildings])

def count_building_points(buildings: list[Building]) -> int:
    return count_building_resources(buildings) * count_building_towers(buildings)

# alternative avec un `match` pour count_building_towers
def count_building_towers_with_match(buildings: list[Building]) -> int:
    towers = 0
    for building in buildings:
        match building:
            case City(): towers += building.towers
            case Factory() | Market(): pass
    return towers


## Question 5. (4 points) -----------------------------------------------------

class Square(Provider): # Provider pour Question 7
    pass

    # Pour Question 6.
    @abstractmethod
    def attempt_build(self, building: Building) -> bool: ...

    # Pour Question 8. Pouvait aussi être une méthode.
    @abstractmethod
    @property
    def building(self) -> Building | None: ...

class Town(Square):
    pass

    # Pour Question 6.
    def attempt_build(self, building: Building) -> bool:
        return False

    # Pour Question 7.
    # overrides Provider.tower_count
    def tower_count(self) -> int:
        return 1

    # Pour Question 8.
    @property
    def building(self) -> Building | None:
        return None

# Alternative (mais moins bien) : répéter contenu dans ResourceSquare et EmptySquare
# Alterantive 2 (un peu moins bien) : tout mettre dans Square
class BuildableSquare(Square):
    # Doit être muable car on doit pouvoir construire pendant la partie.
    # Doit être privée car "[attempt_build] doit être la seule façon dont on
    # peut construire un bâtiment sur une case".
    __building: Building | None # doit être muable

    # attention, pas une init standard
    def __init__(self) -> None:
        super().__init__()
        self.__building = None

    # Pour Question 6.
    def attempt_build(self, building: Building) -> bool:
        if self.__building is None:
            self.__building = building
            return True
        else:
            return False

    # Pour Question 8.
    @property
    def building(self) -> Building | None:
        return self.__building

class ResourceSquare(BuildableSquare):
    resource: Final[ResourceKind]

    ... # init standard
    def __init__(self, resource: ResourceKind):
        super().__init__()
        self.resource = resource

    # Pour Question 7.
    # overrides Provider.resources
    def resources(self) -> frozenset[ResourceKind]:
        return frozenset({self.resource})

class EmptySquare(BuildableSquare):
    pass


## Question 6. (3 points) -----------------------------------------------------

# Voir dans question 5.

# Pas d'alternative externe possible. `__building` doit être privée donc
# attempt_build doit forcément être une méthode.

# Il était cependant possible de remonter `attempt_build` entièrement dans
# Square, du moment qu'elle se basait alors sur un autre aspect polymorphe
# pour décider s'il était autorisé ou non de construire.


## Question 7. (4 points) -----------------------------------------------------

# Les 4 points de cette question sont alloués à la factorisation par rapport à
# la question 3 (entre autres). Si vous avez une implémentation parfaitement
# correcte, mais duplique tout, vous avez reçu 0 à cette question.

# Il y avait ici deux vraiment bonnes solutions. On s'attendait à un
# refactoring de count_building_resources pour pouvoir aussi accepter une
# list[Square]. Il y a deux façons d'accepter autant des `list[Building]` que
# des `list[Square]` : soit en exploitant la variance de `Sequence`, soit en
# utilisant du polymorphisme borné. Dans les deux cas, nous avons besoin d'une
# nouvelle superclasse de `Building` et `Square`

# refactorisation de count_building_resources
def count_resources_variance(providers: Sequence[Provider]) -> int:
    ... # exactement comme avant, en renommant `building(s)` en `provider(s)`
    return 0 # pour que le type-checker soit content dans la version numérique

# refactorisation de count_building_resources
def count_resources_bounded_polymorphism[T: Provider](providers: list[T]) -> int:
    ... # exactement comme avant, en renommant `building(s)` en `provider(s)`
    return 0 # pour que le type-checker soit content dans la version numérique

# Une alternative pour la question 9 était de modifier count_building_resources,
# ou introduire un helper séparé, pour retourner le *set* de ressources en plus
# du nombre. Cependant cela n'empêchait pas de devoir dupliquer presque tout le
# code pour count_square_resources, donc ce n'était pas une solution acceptable
# ici.


## Question 8. (3 points) -----------------------------------------------------

# Idéalement, building était une @property, ce qui permettait d'écrire le
# one-line suivant (je n'y avais pas pensé, mais un certain nombre vous oui !).
def square_buildings(squares: list[Square]) -> list[Building]:
    return [square.building for square in squares if square.building is not None]

# Si building était une méthode, il fallait décomposer un peu plus pour
# satisfaire les exigences de Python.
def square_buildings_alt1(squares: list[Square]) -> list[Building]:
    opt_buildings = [square.building for square in squares]
    return [building for building in opt_buildings if building is not None]

# Encore une autre alternative, sans list comprehension (moins bien dans du
# code réel ; pas pénalisé dans l'examen).
def square_buildings_alt2(squares: list[Square]) -> list[Building]:
    result: list[Building] = []
    for square in squares:
        if square.building is not None:
            result.append(square.building)
    return result

# Alternative avec match; moins bien car on ne peut pas garantir l'exhaustivité
def square_buildings_alt_with_match(squares: list[Square]) -> list[Building]:
    result: list[Building] = []
    for square in squares:
        match square:
            case Town():
                pass
            case BuildableSquare():
                if square.building is not None:
                    result.append(square.building)
    return result


## Question 9. (4 points) -----------------------------------------------------

# 3 points sur 4 de cette question sont alloués à la factorisation par rapport
# à la question 4. Le dernier point est alloué à la mise ensemble des bouts
# déjà faits.

# refactoring de la question 4
def count_towers_variance(providers: Sequence[Provider]) -> int:
    return sum([provider.tower_count() for provider in providers])

# alternative : refactoring par polymorphisme borné
def count_towers_bounded_polymorphism[T: Provider](providers: list[T]) -> int:
    return sum([provider.tower_count() for provider in providers])

def total_points(fiefdom: list[Square]) -> int:
    providers: list[Provider] = []
    providers.extend(fiefdom)
    providers.extend(square_buildings(fiefdom))
    return count_resources_variance(providers) * count_towers_variance(providers)

    # ou avec le polymorphisme borné :
    return count_resources_bounded_polymorphism(providers) * \
        count_towers_bounded_polymorphism(providers)

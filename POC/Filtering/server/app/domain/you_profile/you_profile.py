from typing import Optional, List, Union
from datetime import datetime


class YouProfile:
    """You profle represents your collection of you_profile_utilisateur as an entity."""  # noqa: E501

    def __init__(
        self,
        a_enfant: Optional[Union[int, List[int]]],
        age_begin: Optional[int],
        age_end: Optional[int],
        alcool: Optional[int],
        fumes: Optional[Union[int, List[int]]],
        id_localisation: Optional[Union[int, List[int]]],
        id_nvetudes: Optional[Union[int, List[int]]],
        id_origine: Optional[Union[int, List[int]]],
        id_physique: Optional[Union[int, List[int]]],
        id_profession: Optional[Union[int, List[int]]],
        id_statutmarital: Optional[Union[int, List[int]]],
        id_utilisateur: Optional[int],
        is_converti: Optional[int],
        is_sync: Optional[bool],
        last_modification: Optional[datetime],
        pratiquant: Optional[int],
        salat_pratique: Optional[Union[int, List[int]]],
        taille_begin: Optional[int],
        taille_end: Optional[int],
        v_enfant: Optional[int],
        veil: Optional[Union[int, List[int]]],
        wedding_project: Optional[Union[int, List[int]]],
    ):
        self.a_enfant = a_enfant
        self.age_begin = age_begin
        self.age_end = age_end
        self.alcool = alcool
        self.id_localisation = id_localisation
        self.fumes = fumes
        self.id_nvetudes = id_nvetudes
        self.id_origine = id_origine
        self.id_physique = id_physique
        self.id_profession = id_profession
        self.id_statutmarital = id_statutmarital
        self.id_utilisateur = id_utilisateur
        self.is_converti = is_converti
        self.is_sync = is_sync
        self.last_modification = last_modification
        self.pratiquant = pratiquant
        self.salat_pratique = salat_pratique
        self.taille_begin = taille_begin
        self.taille_end = taille_end
        self.v_enfant = v_enfant
        self.veil = veil
        self.wedding_project = wedding_project

    def __eq__(self, o: object) -> bool:
        if isinstance(o, YouProfile):
            return self.id_utilisateur == o.id_utilisateur

        return False

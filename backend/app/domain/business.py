from pydantic import BaseModel, ConfigDict

from app.enums import BusinessStageEnum, CurrencyUnitEnum


class Business(BaseModel):
    """Business domain model.

    Although this class may be abstract, it is not marked as such to allow instantiations
    of it. This is useful for endpoints were only the parent information is returned, to
    avoid having unnecessary joins in the database query.
    """

    id: int | None = None
    name: str
    location: str
    description: str | None = None
    goal: str | None = None
    stage: BusinessStageEnum
    team_size: int | None = None
    team_description: str | None = None
    user_id: int
    user_position: str | None = None
    extra_info: str | None = None

    model_config = ConfigDict(from_attributes=True)

    def get_information(self) -> str:
        introduction_str = (
            ''
            if self.user_position is None or self.name is None or self.location is None
            else self._get_introduction_str(
                user_position=self.user_position,
                name=self.name,
                location=self.location,
            )
        )
        description_str = (
            ''
            if self.description is None
            else self._get_description_str(self.description)
        )
        team_str = (
            ''
            if self.team_size is None
            else self._get_team_str(self.team_size, self.team_description)
        )
        additional_info_str = self._get_additional_info_str()
        goal_str = '' if self.goal is None else self._get_goal_str(self.goal)
        extra_info_str = '' if self.extra_info is None else self.extra_info
        return (
            f'{introduction_str} {description_str} {additional_info_str} {team_str} '
            f'{goal_str} {extra_info_str}'
        )

    @staticmethod
    def _get_introduction_str(user_position: str, name: str, location: str) -> str:
        return f'Soy el/la {user_position} de {name}, una empresa ubicada en {location}.'

    @staticmethod
    def _get_description_str(description: str) -> str:
        if description is None:
            return ''
        return description

    @staticmethod
    def _get_team_str(team_size: int, team_description: str | None) -> str:
        raise NotImplementedError

    def _get_additional_info_str(self) -> str:
        raise NotImplementedError

    @staticmethod
    def _get_goal_str(goal: str) -> str:
        return f'Nuestro objetivo a corto y medio plazo es el siguiente: {goal}.'


class BusinessIdea(Business):
    competitor_existence: bool | None = None
    competitor_differentiation: str | None = None
    investment: float | None = None
    investment_currency: CurrencyUnitEnum | None = None

    @staticmethod
    def _get_introduction_str(user_position: str, name: str, location: str) -> str:
        return f'Soy el/la fundador de {name}, una empresa ubicada en {location}.'

    @staticmethod
    def _get_description_str(description: str) -> str:
        return (
            f'La empresa todavía no ha salido al mercado. La empresa trata de lo '
            f'siguiente: {description}.'
        )

    @staticmethod
    def _get_team_str(team_size: int, team_description: str | None) -> str:
        return (
            'De momento estoy solo en este proyecto.'
            if team_size == 1
            else (
                f'No estoy solo en este proyecto. Somos {team_size} '
                f'fundadores. {team_description}.'
            )
        )

    def _get_competitor_str(self) -> str:
        return (
            'Aunque existen soluciones similares, nuestro enfoque se diferencia por lo '
            f'siguiente: {self.competitor_differentiation}.'
            if self.competitor_existence
            else 'No existe ninguna solución similar en el mercado.'
        )

    def _get_investment_str(self) -> str:
        return (
            ''
            if self.investment is None or self.investment_currency is None
            else (
                f'El capital inicial será de {self.investment} '
                f'{self.investment_currency}.'
            )
        )

    def _get_additional_info_str(self) -> str:
        return f'{self._get_competitor_str()} {self._get_investment_str()}'


class EstablishedBusiness(Business):
    mission_and_vision: str | None = None
    billing: float | None = None
    billing_currency: CurrencyUnitEnum | None = None
    ebitda: float | None = None
    ebitda_currency: CurrencyUnitEnum | None = None
    profit_margin: float | None = None

    @staticmethod
    def _get_team_str(team_size: int, team_description: str | None) -> str:
        return (
            f'Actualmente contamos con un equipo de {team_size} personas. '
            f'{team_description}.'
        )

    def _get_mission_and_vision_str(self) -> str:
        return (
            ''
            if self.mission_and_vision is None
            else (
                f'Nuestra visión y misión se centran en lo siguiente: '
                f'{self.mission_and_vision}.'
            )
        )

    def _get_billing_str(self) -> str:
        return (
            ''
            if self.billing is None or self.billing_currency is None
            else (
                f'Nuestra facturación actual es de {self.billing} '
                f'{self.billing_currency}, con un EBITDA de {self.ebitda} y un margen '
                f'beneficio del {self.profit_margin}%.'
            )
        )

    def _get_additional_info_str(self) -> str:
        return f'{self._get_mission_and_vision_str()} {self._get_billing_str()}'

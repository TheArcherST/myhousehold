from sqlalchemy import extract, func, select

from myhousehold.core.models import Proposition
from myhousehold.core.models.intents.project import ProjectIntent, Urgency
from myhousehold.reasoners.base import BaseReasoner


class ProteinGoalReasoner(BaseReasoner):
    def premises_selector(self):
        stmt = (select(Proposition)
                .where(extract("date", Proposition.created_at)
                       == extract("date", func.now()))
                .join(Proposition.stream)
                .where(Proposition.stream.record_intent_id.is_not(None))
                .where(Proposition.stream
                       .json_schema.contains({
                            "properties": {
                                "nutrition_info": {
                                    "protein_g": "number",
                                }
                            }
                        })))
        return stmt

    def inference(self, premises: list[Proposition]) -> list[Proposition]:
        total_protein_g = sum(
            (i.json_object
             .get("nutrition_info")
             .get("protein_g"))
            for i in premises
        )

        if total_protein_g < 100:
            msg = f"You need to eat {total_protein_g}g of protein today"
        elif total_protein_g >= 100:
            msg = (f"You finished your protein goal today! You eaten"
                   f" {total_protein_g}g from 100")
        else:
            raise AssertionError()

        return [
            Proposition(
                intent_project=ProjectIntent(
                    urgency=Urgency.MINOR,
                    is_instant=True,
                ),
                json_object={
                    "message": msg,
                },
            ),
        ]

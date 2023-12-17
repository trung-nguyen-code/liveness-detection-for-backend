from typing import List
# from datetime import datetime
from elasticsearch_dsl import Q

from app.constants.user import CommonInput
from app.utils.dict import safe_itemgetter


class YouBuilder:
    def build_categorical_function_score(
        self, functions, search_value, search_field, score=10
    ):
        if isinstance(search_value, list):
            functions.append(
                {
                    "filter": Q(
                        "terms",
                        **{
                            "%s"
                            % (search_field): list(
                                map(lambda x: int(x), search_value)
                            )  # noqa: E501
                        }
                    ),
                    "weight": score,
                }
            )
        else:
            functions.append(
                {
                    "filter": Q(
                        "term", **{"%s" % (search_field): int(search_value)}
                    ),  # noqa: E501
                    "weight": score,
                }
            )
        return functions

    def build_filter(self, queries, search_value, search_field):
        if isinstance(search_value, list):
            queries.append(
                Q(
                    "terms",
                    **{
                        "%s"
                        % (search_field): list(
                            map(lambda x: int(x), search_value)
                        )  # noqa: E501
                    }
                )
            )
        else:
            queries.append(
                Q("term", **{"%s" % (search_field): int(search_value)})
            )  # noqa: E501
        return queries

    def build_common_feature(
        self, feature_value, feature_name, setting, functions, queries
    ):  # noqa: E501
        setting_type = setting["setting_type"]
        score = setting["score"]
        if feature_value and setting_type:
            functions = self.build_categorical_function_score(
                functions, feature_value, feature_name, score
            )
        elif feature_value and not setting_type:
            queries = self.build_filter(queries, feature_value, feature_name)
        return functions, queries

    def parse_common_query(
        self, queries: List, functions: List, input: CommonInput, settings
    ):
        (
            eat_halal,
            is_pratiquant,
            salat_pratique,
            veil,
            want_children,
            has_children,
            family_situation,
            study_level,
            figure,
            fume,
        ) = safe_itemgetter(
            "eat_halal",
            "is_pratiquant",
            "salat_pratique",
            "veil",
            "want_children",
            "has_children",
            "family_situation",
            "study_level",
            "figure",
            "fume",
        )(
            input
        )
        # build eat halal
        # functions, queries = self.build_common_feature(
        #     eat_halal,
        #     "eat_halal",
        #     settings.get("eat_halal"),
        #     functions,
        #     queries,
        # )
        # build religious
        functions, queries = self.build_common_feature(
            is_pratiquant,
            "pratiquant",
            settings.get("religious"),
            functions,
            queries,
        )
        # # build salat pratique
        functions, queries = self.build_common_feature(
            salat_pratique,
            "salat_pratique",
            settings.get("salat_pratique"),
            functions,
            queries,
        )

        #build veil
        if isinstance(veil, list):
            if veil:
                target_veil = veil
                if 1 in veil:
                    target_veil = 2
                elif 2 in veil:
                    target_veil = 1
                functions, queries = self.build_common_feature(
                    target_veil,
                    "veil",
                    settings.get("veil"),
                    functions,
                    queries,
                )
        elif isinstance(veil, int):
            if veil:
                target_veil = veil
                if 1 == veil:
                    target_veil = 2
                elif 2 == veil:
                    target_veil = 1
                functions, queries = self.build_common_feature(
                    target_veil,
                    "veil",
                    settings.get("veil"),
                    functions,
                    queries,
                )
        # # build want children
        # functions, queries = self.build_common_feature(
        #     want_children,
        #     "v_enfant",
        #     settings.get("want_children"),
        #     functions,
        #     queries,
        # )
        # # # build has children
        # functions, queries = self.build_common_feature(
        #     has_children,
        #     "a_enfant",
        #     settings.get("has_children"),
        #     functions,
        #     queries,
        # )
        # # # build family situation
        # functions, queries = self.build_common_feature(
        #     family_situation,
        #     "id_statutmarital",
        #     settings.get("family_situation"),
        #     functions,
        #     queries,
        # )
        # # # build degree
        # functions, queries = self.build_common_feature(
        #     study_level,
        #     "id_nvetudes",
        #     settings.get("degree"),
        #     functions,
        #     queries,
        # )
        # # # build body
        # functions, queries = self.build_common_feature(
        #     figure,
        #     "id_physique",
        #     settings.get("body"),
        #     functions,
        #     queries,
        # )
        # # # build smoke
        # functions, queries = self.build_common_feature(
        #     fume,
        #     "fumes",
        #     settings.get("fume"),
        #     functions,
        #     queries,
        # )

        return functions, queries
    
    def build_range_query(
        self, functions: List, value: int, min_value: str, max_value: str, score=10
    ):  # noqa: E501
        functions.append(
            {
                "script_score": {
                    "script": {
                        "source": """
                                if (doc.containsKey(params.min_value) && !doc[params.min_value].empty && doc[params.min_value].size() > 0 
                                        && doc.containsKey(params.max_value) && !doc[params.max_value].empty && doc[params.max_value].size() > 0) {
                                    if (params.value <= doc[params.min_value].getValue() * 1) {
                                        return params.score * Math.pow(( params.value * 1.0 / doc[params.min_value].getValue() * 1.0), 3);
                                    } else if (params.value >= doc[params.max_value].getValue() * 1) {
                                        return params.score * Math.pow(( doc[params.max_value].getValue() * 1.0 / params.value * 1.0), 3);
                                    } else {
                                        return params.score;
                                    }
                                } else {
                                    return 0;
                                }
                            """  # noqa: E501
                        ,
                        "params": {
                            "min_value": min_value,
                            "max_value": max_value,
                            "value": value,
                            "score": score
                        },  # noqa: E501
                    }
                }
            }
        )
        return functions

    



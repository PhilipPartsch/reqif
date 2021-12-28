from typing import List, Optional

from reqif.models.reqif_spec_object_type import (
    ReqIFSpecObjectType,
    SpecAttributeDefinition,
)
from reqif.models.reqif_types import SpecObjectAttributeType


class SpecObjectTypeParser:
    @staticmethod
    def parse(spec_object_type_xml) -> ReqIFSpecObjectType:
        assert (
            spec_object_type_xml.tag == "SPEC-OBJECT-TYPE"
        ), f"{spec_object_type_xml}"
        attribute_map = {}

        xml_attributes = spec_object_type_xml.attrib
        spec_description: Optional[str] = (
            xml_attributes["DESC"] if "DESC" in xml_attributes else None
        )
        try:
            spec_type_id = xml_attributes["IDENTIFIER"]
        except Exception:
            raise NotImplementedError from None
        try:
            spec_last_change = xml_attributes["LAST-CHANGE"]
        except Exception:
            raise NotImplementedError from None
        try:
            spec_type_long_name = xml_attributes["LONG-NAME"]
        except Exception:
            raise NotImplementedError from None

        spec_attributes = list(spec_object_type_xml)[0]
        attribute_definitions: List[SpecAttributeDefinition] = []
        for attribute_definition in spec_attributes:
            long_name = attribute_definition.attrib["LONG-NAME"]
            identifier = attribute_definition.attrib["IDENTIFIER"]
            description: Optional[str] = (
                attribute_definition.attrib["DESC"]
                if "DESC" in attribute_definition.attrib
                else None
            )
            last_change = (
                attribute_definition.attrib["LAST-CHANGE"]
                if "LAST-CHANGE" in attribute_definition.attrib
                else None
            )
            editable = (
                attribute_definition.attrib["IS-EDITABLE"]
                if "IS-EDITABLE" in attribute_definition.attrib
                else None
            )
            default_value: Optional[str] = None
            if attribute_definition.tag == "ATTRIBUTE-DEFINITION-STRING":
                attribute_type = SpecObjectAttributeType.STRING
                try:
                    datatype_definition = (
                        attribute_definition.find("TYPE")
                        .find("DATATYPE-DEFINITION-STRING-REF")
                        .text
                    )
                except Exception:
                    raise NotImplementedError(attribute_definition) from None

                xml_default_value = attribute_definition.find("DEFAULT-VALUE")
                if xml_default_value is not None:
                    xml_attribute_value = xml_default_value.find(
                        "ATTRIBUTE-VALUE-STRING"
                    )
                    if xml_attribute_value is not None:
                        default_value = xml_attribute_value.attrib["THE-VALUE"]

            elif attribute_definition.tag == "ATTRIBUTE-DEFINITION-INTEGER":
                attribute_type = SpecObjectAttributeType.INTEGER
                try:
                    datatype_definition = (
                        attribute_definition.find("TYPE")
                        .find("DATATYPE-DEFINITION-INTEGER-REF")
                        .text
                    )
                except Exception as exception:
                    raise NotImplementedError(
                        attribute_definition
                    ) from exception

                xml_default_value = attribute_definition.find("DEFAULT-VALUE")
                if xml_default_value is not None:
                    xml_attribute_value = xml_default_value.find(
                        "ATTRIBUTE-VALUE-INTEGER"
                    )
                    assert xml_attribute_value is not None
                    default_value = xml_attribute_value.attrib["THE-VALUE"]

            elif attribute_definition.tag == "ATTRIBUTE-DEFINITION-BOOLEAN":
                attribute_type = SpecObjectAttributeType.BOOLEAN
                try:
                    datatype_definition = (
                        attribute_definition.find("TYPE")
                        .find("DATATYPE-DEFINITION-BOOLEAN-REF")
                        .text
                    )
                except Exception as exception:
                    raise NotImplementedError(
                        attribute_definition
                    ) from exception

            elif attribute_definition.tag == "ATTRIBUTE-DEFINITION-XHTML":
                attribute_type = SpecObjectAttributeType.XHTML
                try:
                    datatype_definition = (
                        attribute_definition.find("TYPE")
                        .find("DATATYPE-DEFINITION-XHTML-REF")
                        .text
                    )
                except Exception as exception:
                    raise NotImplementedError(
                        attribute_definition
                    ) from exception
            elif attribute_definition.tag == "ATTRIBUTE-DEFINITION-ENUMERATION":
                attribute_type = SpecObjectAttributeType.ENUMERATION
                try:
                    datatype_definition = (
                        attribute_definition.find("TYPE")
                        .find("DATATYPE-DEFINITION-ENUMERATION-REF")
                        .text
                    )
                except Exception as exception:
                    raise NotImplementedError(
                        attribute_definition
                    ) from exception
            else:
                raise NotImplementedError(attribute_definition) from None
            attribute_definition = SpecAttributeDefinition(
                attribute_type=attribute_type,
                description=description,
                identifier=identifier,
                last_change=last_change,
                datatype_definition=datatype_definition,
                long_name=long_name,
                editable=editable,
                default_value=default_value,
            )
            attribute_definitions.append(attribute_definition)
            attribute_map[identifier] = long_name

        return ReqIFSpecObjectType(
            description=spec_description,
            identifier=spec_type_id,
            last_change=spec_last_change,
            long_name=spec_type_long_name,
            attribute_definitions=attribute_definitions,
            attribute_map=attribute_map,
        )

    @staticmethod
    def unparse(spec_type: ReqIFSpecObjectType) -> str:
        output = ""

        output += "        " "<SPEC-OBJECT-TYPE"
        if spec_type.description is not None:
            output += f' DESC="{spec_type.description}"'
        output += (
            f' IDENTIFIER="{spec_type.identifier}"'
            f' LAST-CHANGE="{spec_type.last_change}"'
            f' LONG-NAME="{spec_type.long_name}"'
            f">"
            "\n"
        )

        output += "          <SPEC-ATTRIBUTES>\n"

        for attribute in spec_type.attribute_definitions:
            output += (
                "            "
                "<"
                f"{attribute.attribute_type.get_spec_type_tag()}"
            )
            if attribute.description:
                output += f' DESC="{attribute.description}"'

            output += f' IDENTIFIER="{attribute.identifier}"'
            if attribute.last_change:
                output += f' LAST-CHANGE="{attribute.last_change}"'
            output += f' LONG-NAME="{attribute.long_name}"'
            if attribute.editable is not None:
                editable_value = "true" if attribute.editable else "false"
                output += f' IS-EDITABLE="{editable_value}"'
            output += ">" "\n"

            if attribute.default_value:
                output += (
                    "              <DEFAULT-VALUE>\n"
                    f"                "
                    f"<{attribute.attribute_type.get_attribute_value_tag()}"
                    f' THE-VALUE="{attribute.default_value}"/>\n'
                    "              </DEFAULT-VALUE>\n"
                )
            output += "              <TYPE>\n"
            output += (
                "                "
                f"<{attribute.attribute_type.get_definition_tag()}>"
                f"{attribute.datatype_definition}"
                f"</{attribute.attribute_type.get_definition_tag()}>"
                "\n"
            )
            output += "              </TYPE>\n"
            output += "            </"
            output += f"{attribute.attribute_type.get_spec_type_tag()}"
            output += ">\n"

        output += "          </SPEC-ATTRIBUTES>\n"

        output += "        </SPEC-OBJECT-TYPE>\n"

        return output
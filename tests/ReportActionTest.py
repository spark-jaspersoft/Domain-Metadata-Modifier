'''
Created on Aug 10, 2017

@author: stevepark
'''
import unittest
import os
from lxml import etree
from unittest.mock import MagicMock, call
from metadata.ReportAction import ReportAction
from metadata.Common import Common

class ReportActionTest(unittest.TestCase):
    
    common = Common()
    
    VIEW_STATE_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<unifiedState>
  <crosstabState>
    <columnGroups>
      <queryDimension fieldName="name1"/>
    </columnGroups>
    <rowGroups>
      <queryDimension fieldName="name3"/>
    </rowGroups>
  </crosstabState>
  <measures>
    <measure fieldName="name2"/>
  </measures>
  <subFilterList>
    <subFilter id="filter_1" letter="A" sourceString="DYNAMIC">
      <expressionString>name1 == 'value'</expressionString>
      <parameterizedExpressionString>name1 == name1_1</parameterizedExpressionString>
    </subFilter>
  </subFilterList>
</unifiedState>
"""
    VIEW_CROSSTAB_JRXML_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
    <parameter name="REPORT_TITLE" class="java.lang.String" isForPrompting="false">
        <property name="net.sf.jasperreports.data.cache.included" value="true"/>
        <defaultValueExpression><![CDATA[null]]></defaultValueExpression>
    </parameter>
    <parameter name="Collator" class="java.text.Collator" isForPrompting="false">
        <defaultValueExpression><![CDATA[java.text.Collator.getInstance($P{REPORT_LOCALE})]]></defaultValueExpression>
    </parameter>
  <field name="public_store.name1"/>
  <field name="name1"/>
  <field name="name1__DISCRIMINATOR"/>
  <field name="public_store.name2"/>
  <field name="name2"/>
  <field name="name2__DISCRIMINATOR"/>
  <field name="public_store.name3"/>
  <field name="name3"/>
  <field name="name3__DISCRIMINATOR"/>
    <summary>
        <band height="25" splitType="Stretch">
            <crosstab>
                <crosstabParameter name="CrosstabRowGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(2)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabParameter name="CrosstabColumnGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(2)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabDataset isDataPreSorted="true"/>
                <rowGroup name="name1" width="125" headerPosition="Stretch">
                </rowGroup>
                <rowGroup name="name3" width="125" headerPosition="Stretch">
                </rowGroup>
                <columnGroup name="name2" height="20" headerPosition="Stretch">
                </columnGroup>
                <columnGroup name="Measures" height="20" headerPosition="Stretch">
                    <crosstabHeader>
                        <cellContents style="CrosstabBaseCellStyle">
                            <textField isStretchWithOverflow="true">
                                <textFieldExpression><![CDATA["Name3"]]></textFieldExpression>
                                <hyperlinkTooltipExpression><![CDATA["Name3"]]></hyperlinkTooltipExpression>
                            </textField>
                        </cellContents>
                    </crosstabHeader>
                </columnGroup>
                <measure name="CROSSTAB_TOTAL_DISCRIMINATOR" class="java.lang.Boolean" calculation="First">
                    <measureExpression><![CDATA[Boolean.FALSE || $F{name1__DISCRIMINATOR} || $F{name2__DISCRIMINATOR} || $F{name3__DISCRIMINATOR}]]></measureExpression>
                </measure>
            </crosstab>
        </band>
    </summary>
</jasperReport>
"""
    VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
    <parameter name="REPORT_TITLE" class="java.lang.String" isForPrompting="false">
        <property name="net.sf.jasperreports.data.cache.included" value="true"/>
        <defaultValueExpression><![CDATA[null]]></defaultValueExpression>
    </parameter>
    <parameter name="Collator" class="java.text.Collator" isForPrompting="false">
        <defaultValueExpression><![CDATA[java.text.Collator.getInstance($P{REPORT_LOCALE})]]></defaultValueExpression>
    </parameter>
  <field name="name1__DISCRIMINATOR"/>
  <field name="public_store.name2"/>
  <field name="name2"/>
  <field name="name2__DISCRIMINATOR"/>
  <field name="public_store.name3"/>
  <field name="name3"/>
  <field name="name3__DISCRIMINATOR"/>
    <summary>
        <band height="25" splitType="Stretch">
            <crosstab>
                <crosstabParameter name="CrosstabRowGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(1)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabParameter name="CrosstabColumnGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(2)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabDataset isDataPreSorted="true"/>
                <rowGroup name="name3" width="125" headerPosition="Stretch">
                </rowGroup>
                <columnGroup name="name2" height="20" headerPosition="Stretch">
                </columnGroup>
                <columnGroup name="Measures" height="20" headerPosition="Stretch">
                    <crosstabHeader>
                        <cellContents style="CrosstabBaseCellStyle">
                            <textField isStretchWithOverflow="true">
                                <textFieldExpression><![CDATA["Name3"]]></textFieldExpression>
                                <hyperlinkTooltipExpression><![CDATA["Name3"]]></hyperlinkTooltipExpression>
                            </textField>
                        </cellContents>
                    </crosstabHeader>
                </columnGroup>
                <measure name="CROSSTAB_TOTAL_DISCRIMINATOR" class="java.lang.Boolean" calculation="First">
                    <measureExpression><![CDATA[Boolean.FALSE || $F{name1__DISCRIMINATOR} || $F{name2__DISCRIMINATOR} || $F{name3__DISCRIMINATOR}]]></measureExpression>
                </measure>
            </crosstab>
        </band>
    </summary>
</jasperReport>
"""
    VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME2 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
    <parameter name="REPORT_TITLE" class="java.lang.String" isForPrompting="false">
        <property name="net.sf.jasperreports.data.cache.included" value="true"/>
        <defaultValueExpression><![CDATA[null]]></defaultValueExpression>
    </parameter>
    <parameter name="Collator" class="java.text.Collator" isForPrompting="false">
        <defaultValueExpression><![CDATA[java.text.Collator.getInstance($P{REPORT_LOCALE})]]></defaultValueExpression>
    </parameter>
  <field name="public_store.name1"/>
  <field name="name1"/>
  <field name="name1__DISCRIMINATOR"/>
  <field name="name2__DISCRIMINATOR"/>
  <field name="public_store.name3"/>
  <field name="name3"/>
  <field name="name3__DISCRIMINATOR"/>
    <summary>
        <band height="25" splitType="Stretch">
            <crosstab>
                <crosstabParameter name="CrosstabRowGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(2)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabParameter name="CrosstabColumnGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(1)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabDataset isDataPreSorted="true"/>
                <rowGroup name="name1" width="125" headerPosition="Stretch">
                </rowGroup>
                <rowGroup name="name3" width="125" headerPosition="Stretch">
                </rowGroup>
                <columnGroup name="Measures" height="20" headerPosition="Stretch">
                    <crosstabHeader>
                        <cellContents style="CrosstabBaseCellStyle">
                            <textField isStretchWithOverflow="true">
                                <textFieldExpression><![CDATA["Name3"]]></textFieldExpression>
                                <hyperlinkTooltipExpression><![CDATA["Name3"]]></hyperlinkTooltipExpression>
                            </textField>
                        </cellContents>
                    </crosstabHeader>
                </columnGroup>
                <measure name="CROSSTAB_TOTAL_DISCRIMINATOR" class="java.lang.Boolean" calculation="First">
                    <measureExpression><![CDATA[Boolean.FALSE || $F{name1__DISCRIMINATOR} || $F{name2__DISCRIMINATOR} || $F{name3__DISCRIMINATOR}]]></measureExpression>
                </measure>
            </crosstab>
        </band>
    </summary>
</jasperReport>
"""
    VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1_OR_NAME3 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd">
    <parameter name="REPORT_TITLE" class="java.lang.String" isForPrompting="false">
        <property name="net.sf.jasperreports.data.cache.included" value="true"/>
        <defaultValueExpression><![CDATA[null]]></defaultValueExpression>
    </parameter>
    <parameter name="Collator" class="java.text.Collator" isForPrompting="false">
        <defaultValueExpression><![CDATA[java.text.Collator.getInstance($P{REPORT_LOCALE})]]></defaultValueExpression>
    </parameter>
  <field name="name1__DISCRIMINATOR"/>
  <field name="public_store.name2"/>
  <field name="name2"/>
  <field name="name2__DISCRIMINATOR"/>
  <field name="name3__DISCRIMINATOR"/>
    <summary>
        <band height="25" splitType="Stretch">
            <crosstab>
                <crosstabParameter name="CrosstabRowGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(1)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabParameter name="CrosstabColumnGroupsCount" class="java.lang.Integer">
                    <parameterValueExpression><![CDATA[new Integer(2)]]></parameterValueExpression>
                </crosstabParameter>
                <crosstabDataset isDataPreSorted="true"/>
                <rowGroup name="DUMMY" width="0" headerPosition="Stretch">
                    <bucket class="java.lang.Comparable">
                        <bucketExpression><![CDATA[null]]></bucketExpression>
                    </bucket>
                    <crosstabRowHeader>
                        <cellContents/>
                    </crosstabRowHeader>
                    <crosstabTotalRowHeader>
                        <cellContents/>
                    </crosstabTotalRowHeader>
                </rowGroup><columnGroup name="name2" height="20" headerPosition="Stretch">
                </columnGroup>
                <columnGroup name="Measures" height="20" headerPosition="Stretch">
                    </columnGroup>
                <measure name="CROSSTAB_TOTAL_DISCRIMINATOR" class="java.lang.Boolean" calculation="First">
                    <measureExpression><![CDATA[Boolean.FALSE || $F{name1__DISCRIMINATOR} || $F{name2__DISCRIMINATOR} || $F{name3__DISCRIMINATOR}]]></measureExpression>
                </measure>
            </crosstab>
        </band>
    </summary>
</jasperReport>
"""
    VIEW_TABLE_JRXML_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd" name="Very Simple Table View Report" pageWidth="612" pageHeight="792" whenNoDataType="NoPages" columnWidth="572" leftMargin="20" rightMargin="20" topMargin="20" bottomMargin="20" isFloatColumnFooter="true" uuid="07f1d5f2-336a-495e-acbb-1adb53af5138">
    <subDataset name="tableDataset" whenResourceMissingType="Key" uuid="c54db883-7e36-4c64-a435-5da016b49c56">
        <property name="net.sf.jasperreports.create.sort.fields.for.groups" value="true"/>
        <field name="name1" class="java.lang.String">
            <property name="fieldType" value="LEVEL"/>
            <property name="level" value="name1"/>
        </field>
        <field name="_detail_level__name2" class="java.lang.String">
            <property name="fieldType" value="LEVEL_MEASURE"/>
            <property name="level" value="_detail_level_"/>
            <property name="measure" value="name2"/>
        </field>
        <field name="_detail_level__name3" class="java.lang.String">
            <property name="fieldType" value="LEVEL_MEASURE"/>
            <property name="level" value="_detail_level_"/>
            <property name="measure" value="name3"/>
        </field>
        <group name="name1" minHeightToStartNewPage="60">
            <groupExpression><![CDATA[$F{name1}]]></groupExpression>
        </group>
    </subDataset>
    <summary>
        <band height="25" splitType="Stretch">
            <componentElement>
                <reportElement style="TableFrameStyle" x="0" y="0" width="250" height="25" uuid="55ead189-df42-4edb-94e6-0ab4f3f8f232"/>
                <c:table xmlns:c="http://jasperreports.sourceforge.net/jasperreports/components" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports/components http://jasperreports.sourceforge.net/xsd/components.xsd" whenNoDataType="AllSectionsNoDetail">
                    <c:columnGroup width="250" uuid="857fe84f-e7a4-475d-92ef-8881b556e3cc">
                        <c:groupHeader groupName="name1">
                            <c:cell style="TableGroupHeaderFrameStyle" height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true" bookmarkLevel="1">
                                    <reportElement style="TableGroupHeaderTextStyle" x="0" y="0" width="250" height="25" uuid="4deae992-1b5a-48b0-bbc3-62ce053be8c5">
                                        <property name="net.sf.jasperreports.components.condition.type" value="Text"/>
                                    </reportElement>
                                    <textFieldExpression><![CDATA[AdhocEngineServiceImpl.getInstance().formatValue($F{name1}, null,"java.lang.String", $P{REPORT_LOCALE}, $P{REPORT_TIME_ZONE})]]></textFieldExpression>
                                </textField>
                            </c:cell>
                        </c:groupHeader>
                        <c:column width="125" uuid="b048961c-ae4c-4ce9-8aed-e76c0e6fbe3c">
                            <c:columnHeader height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement style="TableColumnHeaderTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="733f3499-739f-47f6-9703-80a7d2685e09">
                                        <property name="net.sf.jasperreports.components.condition.type" value="Text"/>
                                    </reportElement>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA["Name 2"]]></textFieldExpression>
                                </textField>
                            </c:columnHeader>
                            <c:detailCell height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement key="textField" style="TableDetailTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="906198fb-a56c-4b34-a802-ab921bdd4887"/>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA[$F{_detail_level__name2}]]></textFieldExpression>
                                    <patternExpression><![CDATA[$P{_name2_AdHocMask}]]></patternExpression>
                                </textField>
                            </c:detailCell>
                        </c:column>
                        <c:column width="125" uuid="b048961c-ae4c-4ce9-8aed-e76c0e6fbe3c">
                            <c:columnHeader height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement style="TableColumnHeaderTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="733f3499-739f-47f6-9703-80a7d2685e09">
                                        <property name="net.sf.jasperreports.components.condition.type" value="Text"/>
                                    </reportElement>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA["Name 3"]]></textFieldExpression>
                                </textField>
                            </c:columnHeader>
                            <c:detailCell height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement key="textField" style="TableDetailTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="906198fb-a56c-4b34-a802-ab921bdd4887"/>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA[$F{_detail_level__name3}]]></textFieldExpression>
                                    <patternExpression><![CDATA[$P{_name3_AdHocMask}]]></patternExpression>
                                </textField>
                            </c:detailCell>
                        </c:column>
                    </c:columnGroup>
                </c:table>
            </componentElement>
        </band>
    </summary>
</jasperReport>
"""
    VIEW_TABLE_JRXML_FILE_WITHOUT_NAME1 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd" name="Very Simple Table View Report" pageWidth="612" pageHeight="792" whenNoDataType="NoPages" columnWidth="572" leftMargin="20" rightMargin="20" topMargin="20" bottomMargin="20" isFloatColumnFooter="true" uuid="07f1d5f2-336a-495e-acbb-1adb53af5138">
    <subDataset name="tableDataset" whenResourceMissingType="Key" uuid="c54db883-7e36-4c64-a435-5da016b49c56">
        <property name="net.sf.jasperreports.create.sort.fields.for.groups" value="true"/>
        <field name="_detail_level__name2" class="java.lang.String">
            <property name="fieldType" value="LEVEL_MEASURE"/>
            <property name="level" value="_detail_level_"/>
            <property name="measure" value="name2"/>
        </field>
        <field name="_detail_level__name3" class="java.lang.String">
            <property name="fieldType" value="LEVEL_MEASURE"/>
            <property name="level" value="_detail_level_"/>
            <property name="measure" value="name3"/>
        </field>
        </subDataset>
    <summary>
        <band height="25" splitType="Stretch">
            <componentElement>
                <reportElement style="TableFrameStyle" x="0" y="0" width="250" height="25" uuid="55ead189-df42-4edb-94e6-0ab4f3f8f232"/>
                <c:table xmlns:c="http://jasperreports.sourceforge.net/jasperreports/components" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports/components http://jasperreports.sourceforge.net/xsd/components.xsd" whenNoDataType="AllSectionsNoDetail">
                    <c:columnGroup width="250" uuid="857fe84f-e7a4-475d-92ef-8881b556e3cc">
                        <c:column width="125" uuid="b048961c-ae4c-4ce9-8aed-e76c0e6fbe3c">
                            <c:columnHeader height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement style="TableColumnHeaderTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="733f3499-739f-47f6-9703-80a7d2685e09">
                                        <property name="net.sf.jasperreports.components.condition.type" value="Text"/>
                                    </reportElement>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA["Name 2"]]></textFieldExpression>
                                </textField>
                            </c:columnHeader>
                            <c:detailCell height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement key="textField" style="TableDetailTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="906198fb-a56c-4b34-a802-ab921bdd4887"/>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA[$F{_detail_level__name2}]]></textFieldExpression>
                                    <patternExpression><![CDATA[$P{_name2_AdHocMask}]]></patternExpression>
                                </textField>
                            </c:detailCell>
                        </c:column>
                        <c:column width="125" uuid="b048961c-ae4c-4ce9-8aed-e76c0e6fbe3c">
                            <c:columnHeader height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement style="TableColumnHeaderTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="733f3499-739f-47f6-9703-80a7d2685e09">
                                        <property name="net.sf.jasperreports.components.condition.type" value="Text"/>
                                    </reportElement>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA["Name 3"]]></textFieldExpression>
                                </textField>
                            </c:columnHeader>
                            <c:detailCell height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement key="textField" style="TableDetailTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="906198fb-a56c-4b34-a802-ab921bdd4887"/>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA[$F{_detail_level__name3}]]></textFieldExpression>
                                    <patternExpression><![CDATA[$P{_name3_AdHocMask}]]></patternExpression>
                                </textField>
                            </c:detailCell>
                        </c:column>
                    </c:columnGroup>
                </c:table>
            </componentElement>
        </band>
    </summary>
</jasperReport>
"""
    VIEW_TABLE_JRXML_FILE_WITHOUT_NAME2 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd" name="Very Simple Table View Report" pageWidth="612" pageHeight="792" whenNoDataType="NoPages" columnWidth="572" leftMargin="20" rightMargin="20" topMargin="20" bottomMargin="20" isFloatColumnFooter="true" uuid="07f1d5f2-336a-495e-acbb-1adb53af5138">
    <subDataset name="tableDataset" whenResourceMissingType="Key" uuid="c54db883-7e36-4c64-a435-5da016b49c56">
        <property name="net.sf.jasperreports.create.sort.fields.for.groups" value="true"/>
        <field name="name1" class="java.lang.String">
            <property name="fieldType" value="LEVEL"/>
            <property name="level" value="name1"/>
        </field>
        <field name="_detail_level__name3" class="java.lang.String">
            <property name="fieldType" value="LEVEL_MEASURE"/>
            <property name="level" value="_detail_level_"/>
            <property name="measure" value="name3"/>
        </field>
        <group name="name1" minHeightToStartNewPage="60">
            <groupExpression><![CDATA[$F{name1}]]></groupExpression>
        </group>
    </subDataset>
    <summary>
        <band height="25" splitType="Stretch">
            <componentElement>
                <reportElement style="TableFrameStyle" x="0" y="0" width="250" height="25" uuid="55ead189-df42-4edb-94e6-0ab4f3f8f232"/>
                <c:table xmlns:c="http://jasperreports.sourceforge.net/jasperreports/components" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports/components http://jasperreports.sourceforge.net/xsd/components.xsd" whenNoDataType="AllSectionsNoDetail">
                    <c:columnGroup width="125" uuid="857fe84f-e7a4-475d-92ef-8881b556e3cc">
                        <c:groupHeader groupName="name1">
                            <c:cell style="TableGroupHeaderFrameStyle" height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true" bookmarkLevel="1">
                                    <reportElement style="TableGroupHeaderTextStyle" x="0" y="0" width="125" height="25" uuid="4deae992-1b5a-48b0-bbc3-62ce053be8c5">
                                        <property name="net.sf.jasperreports.components.condition.type" value="Text"/>
                                    </reportElement>
                                    <textFieldExpression><![CDATA[AdhocEngineServiceImpl.getInstance().formatValue($F{name1}, null,"java.lang.String", $P{REPORT_LOCALE}, $P{REPORT_TIME_ZONE})]]></textFieldExpression>
                                </textField>
                            </c:cell>
                        </c:groupHeader>
                        <c:column width="125" uuid="b048961c-ae4c-4ce9-8aed-e76c0e6fbe3c">
                            <c:columnHeader height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement style="TableColumnHeaderTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="733f3499-739f-47f6-9703-80a7d2685e09">
                                        <property name="net.sf.jasperreports.components.condition.type" value="Text"/>
                                    </reportElement>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA["Name 3"]]></textFieldExpression>
                                </textField>
                            </c:columnHeader>
                            <c:detailCell height="25">
                                <textField isStretchWithOverflow="true" isBlankWhenNull="true">
                                    <reportElement key="textField" style="TableDetailTextStyle" stretchType="RelativeToBandHeight" x="0" y="0" width="125" height="25" uuid="906198fb-a56c-4b34-a802-ab921bdd4887"/>
                                    <textElement textAlignment="Left"/>
                                    <textFieldExpression><![CDATA[$F{_detail_level__name3}]]></textFieldExpression>
                                    <patternExpression><![CDATA[$P{_name3_AdHocMask}]]></patternExpression>
                                </textField>
                            </c:detailCell>
                        </c:column>
                    </c:columnGroup>
                </c:table>
            </componentElement>
        </band>
    </summary>
</jasperReport>
"""
    STATIC_JRXML_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd" name="Very_Simple_Domain_Driven_Static_Report" pageWidth="595" pageHeight="842" columnWidth="555" leftMargin="20" rightMargin="20" topMargin="20" bottomMargin="20" uuid="b21142d2-dbe4-4b28-afc0-f59f7c57f677">
    <property name="ireport.domainUri" value="/Domain_Test"/>
    <property name="com.jaspersoft.studio.data.defaultdataadapter" value="Domain Test"/>
    <parameter name="name1_0" class="java.util.Collection" nestedType="java.lang.String">
        <property name="inputControl" value="true"/>
        <parameterDescription><![CDATA[name1]]></parameterDescription>
        <defaultValueExpression><![CDATA[java.util.Arrays.asList(new java.lang.String[] {"Something","Something Else"})]]></defaultValueExpression>
    </parameter>
    <parameter name="LoggedInUser" class="com.jaspersoft.jasperserver.api.metadata.user.domain.User" isForPrompting="false"/>
    <parameter name="LoggedInUsername" class="java.lang.String" isForPrompting="false"/>
    <queryString language="domain"><![CDATA[<query>
    <queryFields>
        <queryField id="name1"/>
        <queryField id="name2"/>
        </queryFields>
    <queryFilterString>name1 in name1_0 OR name2 == 'a big mess'</queryFilterString>
</query>
]]></queryString>
    <field name="name1" class="java.lang.String">
        <fieldDescription><![CDATA[name1]]></fieldDescription>
    </field>
    <field name="name2" class="java.math.BigDecimal">
        <fieldDescription><![CDATA[name2]]></fieldDescription>
    </field>
    <group name="name2">
        <groupExpression><![CDATA[$F{name2}]]></groupExpression>
        <groupHeader>
            <band height="30">
                <textField>
                    <reportElement mode="Opaque" x="100" y="0" width="100" height="30" forecolor="#FFFFFF" backcolor="#878686" uuid="19d713f0-ed82-43ef-9dbc-de309d46e30a"/>
                    <textElement verticalAlignment="Middle">
                        <font size="12" isBold="true"/>
                    </textElement>
                    <textFieldExpression><![CDATA[$F{name2}]]></textFieldExpression>
                </textField>
                <staticText>
                    <reportElement mode="Opaque" x="0" y="0" width="100" height="30" forecolor="#FFFFFF" backcolor="#878686" uuid="19c707b3-40a9-4291-969e-9c5a2f025c74"/>
                    <textElement verticalAlignment="Middle">
                        <font size="12" isBold="true"/>
                    </textElement>
                    <text><![CDATA[Name 2:]]></text>
                </staticText>
            </band>
        </groupHeader>
    </group>
    <background>
        <band splitType="Stretch"/>
    </background>
    <title>
        <band height="79" splitType="Stretch">
            <staticText>
                <reportElement x="0" y="0" width="555" height="79" uuid="13394254-1db7-4e4d-868d-621b6c749965"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="24" isBold="true"/>
                </textElement>
                <text><![CDATA[Domain Driven Static Report]]></text>
            </staticText>
        </band>
    </title>
    <columnHeader>
        <band height="30" splitType="Stretch">
            <staticText>
                <reportElement x="0" y="0" width="278" height="30" uuid="0ae62797-b89b-4c22-930b-869ff41d8062"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="14" isBold="true"/>
                </textElement>
                <text><![CDATA[Name 1]]></text>
            </staticText>
        </band>
    </columnHeader>
    <detail>
        <band height="30" splitType="Stretch">
            <textField>
                <reportElement x="277" y="0" width="278" height="30" uuid="0e18fa5d-cc25-4f50-b012-44db0bc2a868"/>
                <textFieldExpression><![CDATA[$F{name1}]]></textFieldExpression>
            </textField>
            </band>
    </detail>
</jasperReport>
"""
    STATIC_JRXML_FILE_WITHOUT_NAME1 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd" name="Very_Simple_Domain_Driven_Static_Report" pageWidth="595" pageHeight="842" columnWidth="555" leftMargin="20" rightMargin="20" topMargin="20" bottomMargin="20" uuid="b21142d2-dbe4-4b28-afc0-f59f7c57f677">
    <property name="ireport.domainUri" value="/Domain_Test"/>
    <property name="com.jaspersoft.studio.data.defaultdataadapter" value="Domain Test"/>
    <parameter name="LoggedInUser" class="com.jaspersoft.jasperserver.api.metadata.user.domain.User" isForPrompting="false"/>
    <parameter name="LoggedInUsername" class="java.lang.String" isForPrompting="false"/>
    <queryString language="domain"><![CDATA[<query>
    <queryFields>
        <queryField id="name2"/>
        </queryFields>
    <queryFilterString>name2 == 'a big mess'</queryFilterString>
</query>
]]></queryString>
    <field name="name2" class="java.math.BigDecimal">
        <fieldDescription><![CDATA[name2]]></fieldDescription>
    </field>
    <group name="name2">
        <groupExpression><![CDATA[$F{name2}]]></groupExpression>
        <groupHeader>
            <band height="30">
                <textField>
                    <reportElement mode="Opaque" x="100" y="0" width="100" height="30" forecolor="#FFFFFF" backcolor="#878686" uuid="19d713f0-ed82-43ef-9dbc-de309d46e30a"/>
                    <textElement verticalAlignment="Middle">
                        <font size="12" isBold="true"/>
                    </textElement>
                    <textFieldExpression><![CDATA[$F{name2}]]></textFieldExpression>
                </textField>
                <staticText>
                    <reportElement mode="Opaque" x="0" y="0" width="100" height="30" forecolor="#FFFFFF" backcolor="#878686" uuid="19c707b3-40a9-4291-969e-9c5a2f025c74"/>
                    <textElement verticalAlignment="Middle">
                        <font size="12" isBold="true"/>
                    </textElement>
                    <text><![CDATA[Name 2:]]></text>
                </staticText>
            </band>
        </groupHeader>
    </group>
    <background>
        <band splitType="Stretch"/>
    </background>
    <title>
        <band height="79" splitType="Stretch">
            <staticText>
                <reportElement x="0" y="0" width="555" height="79" uuid="13394254-1db7-4e4d-868d-621b6c749965"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="24" isBold="true"/>
                </textElement>
                <text><![CDATA[Domain Driven Static Report]]></text>
            </staticText>
        </band>
    </title>
    <columnHeader>
        <band height="30" splitType="Stretch">
            <staticText>
                <reportElement x="0" y="0" width="278" height="30" uuid="0ae62797-b89b-4c22-930b-869ff41d8062"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="14" isBold="true"/>
                </textElement>
                <text><![CDATA[Name 1]]></text>
            </staticText>
        </band>
    </columnHeader>
    <detail>
        <band height="30" splitType="Stretch">
            </band>
    </detail>
</jasperReport>
"""
    STATIC_JRXML_FILE_WITHOUT_NAME2 = """<?xml version="1.0" encoding="UTF-8"?>
<jasperReport xmlns="http://jasperreports.sourceforge.net/jasperreports" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://jasperreports.sourceforge.net/jasperreports http://jasperreports.sourceforge.net/xsd/jasperreport.xsd" name="Very_Simple_Domain_Driven_Static_Report" pageWidth="595" pageHeight="842" columnWidth="555" leftMargin="20" rightMargin="20" topMargin="20" bottomMargin="20" uuid="b21142d2-dbe4-4b28-afc0-f59f7c57f677">
    <property name="ireport.domainUri" value="/Domain_Test"/>
    <property name="com.jaspersoft.studio.data.defaultdataadapter" value="Domain Test"/>
    <parameter name="name1_0" class="java.util.Collection" nestedType="java.lang.String">
        <property name="inputControl" value="true"/>
        <parameterDescription><![CDATA[name1]]></parameterDescription>
        <defaultValueExpression><![CDATA[java.util.Arrays.asList(new java.lang.String[] {"Something","Something Else"})]]></defaultValueExpression>
    </parameter>
    <parameter name="LoggedInUser" class="com.jaspersoft.jasperserver.api.metadata.user.domain.User" isForPrompting="false"/>
    <parameter name="LoggedInUsername" class="java.lang.String" isForPrompting="false"/>
    <queryString language="domain"><![CDATA[<query>
    <queryFields>
        <queryField id="name1"/>
        </queryFields>
    <queryFilterString>name1 in name1_0</queryFilterString>
</query>
]]></queryString>
    <field name="name1" class="java.lang.String">
        <fieldDescription><![CDATA[name1]]></fieldDescription>
    </field>
    <background>
        <band splitType="Stretch"/>
    </background>
    <title>
        <band height="79" splitType="Stretch">
            <staticText>
                <reportElement x="0" y="0" width="555" height="79" uuid="13394254-1db7-4e4d-868d-621b6c749965"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="24" isBold="true"/>
                </textElement>
                <text><![CDATA[Domain Driven Static Report]]></text>
            </staticText>
        </band>
    </title>
    <columnHeader>
        <band height="30" splitType="Stretch">
            <staticText>
                <reportElement x="0" y="0" width="278" height="30" uuid="0ae62797-b89b-4c22-930b-869ff41d8062"/>
                <textElement textAlignment="Center" verticalAlignment="Middle">
                    <font size="14" isBold="true"/>
                </textElement>
                <text><![CDATA[Name 1]]></text>
            </staticText>
        </band>
    </columnHeader>
    <detail>
        <band height="30" splitType="Stretch">
            <textField>
                <reportElement x="277" y="0" width="278" height="30" uuid="0e18fa5d-cc25-4f50-b012-44db0bc2a868"/>
                <textFieldExpression><![CDATA[$F{name1}]]></textFieldExpression>
            </textField>
            </band>
    </detail>
</jasperReport>
"""
    REPORT_METADATA_FILE = """<?xml version="1.0" encoding="UTF-8"?>
<reportUnit exportedWithPermissions="true">
    <folder/>
    <name>Report_Test</name>
    <mainReport>
        <localResource
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            exportedWithPermissions="false" dataFile="main_jrxml.data" xsi:type="fileResource">
            <folder>/Report_Test_files</folder>
            <name>main_jrxml</name>
            <fileType>jrxml</fileType>
        </localResource>
    </mainReport>
    <dataSource>
        <uri>/Domain_Test</uri>
    </dataSource>
    <inputControl>
        <localResource
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            exportedWithPermissions="false" xsi:type="inputControl">
            <folder>/Report_Test_files</folder>
            <name>name1_1</name>
            <query>
                <localResource exportedWithPermissions="false" xsi:type="query">
                    <folder>/Report_Test_files/name1_1_files</folder>
                    <name>query_name1_1</name>
                    <queryString>&lt;query&gt;
&lt;queryFields&gt;&lt;queryField id="name1"/&gt;&lt;/queryFields&gt;
&lt;/query&gt;</queryString>
                    <dataSource>
                        <uri>/Domain_Test</uri>
                    </dataSource>
                </localResource>
            </query>
            <queryVisibleColumn>name1</queryVisibleColumn>
            <queryValueColumn>name1</queryValueColumn>
        </localResource>
    </inputControl>
</reportUnit>
"""
    REPORT_METADATA_FILE_WITHOUT_NAME1 = """<?xml version="1.0" encoding="UTF-8"?>
<reportUnit exportedWithPermissions="true">
    <folder/>
    <name>Report_Test</name>
    <mainReport>
        <localResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" exportedWithPermissions="false" dataFile="main_jrxml.data" xsi:type="fileResource">
            <folder>/Report_Test_files</folder>
            <name>main_jrxml</name>
            <fileType>jrxml</fileType>
        </localResource>
    </mainReport>
    <dataSource>
        <uri>/Domain_Test</uri>
    </dataSource>
    <inputControl>
        </inputControl>
</reportUnit>"""

    def setUp(self):
        self.report_action = ReportAction()
        self.log = self.common.configureLogging()
        self.curr_folder = '/tmp'
        self.adhocId = 'adhocId'
        files_path = Common.REPO_PATH_SEPARATOR + self.adhocId + '_files'
        self.state_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'stateXML.data'
        self.jrxml_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'mainReportJrxml.data'
        self.table_jrxml_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'mainReportJrxmlTable.data'
        self.static_jrxml_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'main_jrxml.data'
        self.report_metadata_filepath = self.curr_folder + files_path + Common.REPO_PATH_SEPARATOR + 'Report_Test.xml'
        directory = os.path.dirname(self.state_filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(self.state_filepath, 'w') as h1:
            h1.write(self.VIEW_STATE_FILE)
        with open(self.jrxml_filepath, 'w') as h2:
            h2.write(self.VIEW_CROSSTAB_JRXML_FILE)
        with open(self.table_jrxml_filepath, 'w') as h3:
            h3.write(self.VIEW_TABLE_JRXML_FILE)
        with open(self.static_jrxml_filepath, 'w') as h4:
            h4.write(self.STATIC_JRXML_FILE)
        with open(self.report_metadata_filepath, 'w') as h5:
            h5.write(self.REPORT_METADATA_FILE)

    def tearDown(self):
        try:
            os.remove(self.report_metadata_filepath)
            os.remove(self.static_jrxml_filepath)
            os.remove(self.table_jrxml_filepath)
            os.remove(self.jrxml_filepath)
            os.remove(self.state_filepath)
        except OSError:
            pass
            
    def testRemoveFieldFromFieldList(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2a'
        mock_node2.getparent.return_value = mock_root
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name2b'
        mock_node3.getparent.return_value = mock_root
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 'name2__' + Common.DISCRIMINATOR
        node_list = [mock_node1, mock_node2, mock_node3, mock_node4]
        mock_root.xpath = MagicMock(side_effect=[node_list])
        self.report_action.removeFieldFromFieldList(root=mock_root, fieldname='name2', log=self.log)
        calls = [call('//n:field', namespaces=Common.JRXML_NAMESPACE)]
        mock_root.xpath.assert_has_calls(calls, any_order=True)
        calls = [call(mock_node2), call(mock_node3)]
        mock_root.remove.assert_has_calls(calls)
        
    def testInsertDummyRowGroup(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node2 = MagicMock(name='mock_node2')
        mock_node1.getparent.return_value = mock_node2
        mock_node2.index.return_value = 3
        mock_node3 = MagicMock(name='mock_node3')
        mock_node4 = MagicMock(name='mock_node4')
        mock_node3.getparent.return_value = mock_node4
        node_list1 = [mock_node1]
        node_list2 = [mock_node3]
        mock_root.xpath = MagicMock(side_effect=[node_list1, node_list2])
        self.report_action.insertDummyRowGroup(root=mock_root, log=self.log)
        mock_node2.insert.assert_called_once()
        mock_node2.index.assert_called()
        mock_node4.remove.assert_called_once_with(mock_node3)
            
    def testRemoveRowGroupFromCrosstabReport(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2a'
        mock_node2.getparent.return_value = mock_root
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name2b'
        mock_node3.getparent.return_value = mock_root
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 'name2__' + Common.DISCRIMINATOR
        mock_node5 = MagicMock(name='mock_node5')
        mock_node6 = etree.Element('mock_node6')
        mock_node6.text = 'new Integer(55)'
        mock_node5.__getitem__.return_value = mock_node6
        node_list1 = [mock_node1, mock_node2, mock_node3, mock_node4]
        node_list2 = [mock_node5]
        mock_root.xpath = MagicMock(side_effect=[node_list1, node_list2, node_list2, node_list2])
        self.report_action.removeRowGroupFromCrosstab(root=mock_root, fieldname='name2', log=self.log)
        calls = [call('//n:rowGroup', namespaces=Common.JRXML_NAMESPACE)]
        mock_root.xpath.assert_has_calls(calls, any_order=True)
        calls = [call(mock_node2), call(mock_node3)]
        mock_root.remove.assert_has_calls(calls)
        self.assertEqual('new Integer(52)', mock_node6.text, 'column group has incorrect count')
            
    def testRemoveColumnGroupFromCrosstabReport(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2a'
        mock_node2.getparent.return_value = mock_root
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name2b'
        mock_node3.getparent.return_value = mock_root
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 'name2__' + Common.DISCRIMINATOR
        mock_node5 = MagicMock(name='mock_node5')
        mock_node6 = etree.Element('mock_node6')
        mock_node6.text = 'new Integer(55)'
        mock_node5.__getitem__.return_value = mock_node6
        node_list1 = [mock_node1, mock_node2, mock_node3, mock_node4]
        node_list2 = [mock_node5]
        mock_root.xpath = MagicMock(side_effect=[node_list1, node_list2, node_list2, node_list2])
        self.report_action.removeColumnGroupFromCrosstab(root=mock_root, fieldname='name2', log=self.log)
        calls = [call('//n:columnGroup', namespaces=Common.JRXML_NAMESPACE)]
        mock_root.xpath.assert_has_calls(calls, any_order=True)
        calls = [call(mock_node2), call(mock_node3)]
        mock_root.remove.assert_has_calls(calls)
        self.assertEqual('new Integer(52)', mock_node6.text, 'column group has incorrect count')
    
    def testRemoveDetailFieldFromTable(self):
        newColumnWidth = 135
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text.find.return_value = 10
        mock_node2 = MagicMock(name='mock_node2')
        mock_node1.getparent.return_value = mock_node2
        mock_node3 = MagicMock(name='mock_node3')
        mock_node2.getparent.return_value = mock_node3
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 50
        mock_node3.getparent.return_value = mock_node4
        mock_node5 = MagicMock(name='mock_node5')
        mock_node5.get.return_value = newColumnWidth
        mock_node4.getparent.return_value = mock_node5
        mock_node6 = MagicMock(name='mock_node6')
        mock_node7 = MagicMock(name='mock_node7')
        mock_node6.getparent.return_value = mock_node7
        mock_node8 = MagicMock(name='mock_node8')
        mock_node7.getparent.return_value = mock_node8
        mock_node9 = MagicMock(name='mock_node9')
        mock_node8.getparent.return_value = mock_node9
        mock_node9.tag.find.return_value = 0
        node_list1 = [mock_node1]
        node_list2 = [mock_node6]
        mock_root.xpath = MagicMock(side_effect=[node_list1, node_list2])
        self.report_action.removeDetailFieldFromTable(root=mock_root, fieldname='name1', log=self.log)
        mock_node5.remove.assert_called_once_with(mock_node4)
        mock_node6.attrib.__setitem__.assert_called_once_with(Common.WIDTH, newColumnWidth)
        
    def testRemoveGroupFromTable(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node1.getparent.return_value = mock_node2
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name1'
        mock_node4 = MagicMock(name='mock_node4')
        mock_node3.getparent.return_value = mock_node4
        node_list1 = [mock_node1]
        node_list2 = [mock_node3]
        mock_root.xpath = MagicMock(side_effect=[node_list1, node_list2])
        self.report_action.removeFieldFromGroup(root=mock_root, fieldname='name1', log=self.log)
        mock_node2.remove.assert_called_once_with(mock_node1)
        mock_node4.remove.assert_called_once_with(mock_node3)
            
    def testRemoveQueryFieldFromReportQuery(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2a'
        mock_node2.getparent.return_value = mock_root
        mock_node3 = MagicMock(name='mock_node3')
        mock_node3.get.return_value = 'name2b'
        mock_node3.getparent.return_value = mock_root
        mock_node4 = MagicMock(name='mock_node4')
        mock_node4.get.return_value = 'name3'
        mock_node5 = etree.Element('mock_node5')
        mock_node5.text = 'name1 < A AND name2 == name5 AND name3 >= 40 OR name4 != "something"'
        node_list1 = [mock_node1, mock_node2, mock_node3, mock_node4]
        node_list2 = [mock_node5]
        mock_root.xpath = MagicMock(side_effect=[node_list1, node_list2])
        self.report_action.removeQueryFieldFromReportQuery(root=mock_root, fieldname='name2', log=self.log)
        mock_root.xpath.assert_called_with('//queryFilterString')
        calls = [call(mock_node2), call(mock_node3)]
        mock_root.remove.assert_has_calls(calls)
        self.assertEqual('name1 < A AND name3 >= 40 OR name4 != "something"', mock_node5.text, 'query filter string malformed or clause not removed')
            
    def testRemoveFieldFromStateIsMeasure(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2'
        mock_node2.getparent.return_value = mock_root
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect=[node_list, [], [], [], []])
        self.report_action.removeFieldFromState(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node2)
            
    def testRemoveFieldFromStateIsDimension(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.get.return_value = 'name1'
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.get.return_value = 'name2'
        mock_node2.getparent.return_value = mock_root
        node_list = [mock_node1, mock_node2]
        mock_root.xpath = MagicMock(side_effect=[[], node_list, []])
        self.report_action.removeFieldFromState(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node2)
            
    def testRemoveFieldFromStateIsParameter(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.getparent.return_value = mock_root
        mock_node2 = MagicMock(name='mock_node2')
        mock_node2.getparent.return_value = mock_node1
        mock_node2.text.find.return_value = 0
        mock_root.xpath = MagicMock(side_effect=[[], [], [mock_node2]])
        self.report_action.removeFieldFromState(root=mock_root, fieldname='name2', log=self.log)
        mock_root.remove.assert_called_with(mock_node1)
        
    def testRemoveFieldNoMatches(self):
        field_name = 'name4'
        self.report_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertEqual(self.VIEW_STATE_FILE, state_xml, 'state file changed')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE, jrxml_xml, 'jrxml file changed')
            
    def testRemoveFieldMatchesIsMeasure(self):
        field_name = 'name2'
        self.report_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertTrue(state_xml.find(field_name) == -1, 'Measure ' + field_name + ' not removed from state file')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME2, jrxml_xml, 'jrxml file content does not match expected')
            
    def testRemoveFieldMatchesIsDimension(self):
        field_name = 'name1'
        self.report_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertTrue(state_xml.find(field_name) == -1, 'Dimension ' + field_name + ' not removed from state file')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1, jrxml_xml, 'jrxml file content does not match expected')
            
    def testRemoveMultipleFields(self):
        field_name = ['name1','name3']
        self.report_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            for singular in field_name:
                self.assertTrue(state_xml.find(singular) == -1, 'Dimension ' + singular + ' not removed from state file')
        with open(self.jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_CROSSTAB_JRXML_FILE_WITHOUT_NAME1_OR_NAME3, jrxml_xml, 'jrxml file content does not match expected')
            
    def testRemoveFromTableIsGroup(self):
        field_name = 'name1'
        self.report_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.table_jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertTrue(state_xml.find(field_name) == -1, 'Group ' + field_name + ' not removed from state file')
        with open(self.table_jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_TABLE_JRXML_FILE_WITHOUT_NAME1, jrxml_xml, 'jrxml file content does not match expected')
            
    def testRemoveFromTableIsField(self):
        field_name = 'name2'
        self.report_action.removeField(state_filename=self.state_filepath, jrxml_filename=self.table_jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.state_filepath) as h:
            state_xml = h.read()
            self.assertTrue(state_xml.find(field_name) == -1, 'Field ' + field_name + ' not removed from state file')
        with open(self.table_jrxml_filepath) as h1:
            jrxml_xml = h1.read()
            self.assertEqual(self.VIEW_TABLE_JRXML_FILE_WITHOUT_NAME2, jrxml_xml, 'jrxml file content does not match expected')
            
    def testRemoveFieldFromStaticReport(self):
        field_name = 'name1'
        self.report_action.removeField(state_filename=None, jrxml_filename=self.static_jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.static_jrxml_filepath) as h:
            jrxml_xml = h.read()
            self.assertEqual(self.STATIC_JRXML_FILE_WITHOUT_NAME1, jrxml_xml, 'jrxml file content does not match expected')
            
    def testRemoveGroupFromStaticReport(self):
        field_name = 'name2'
        self.report_action.removeField(state_filename=None, jrxml_filename=self.static_jrxml_filepath, fieldname=field_name, log=self.log)
        with open(self.static_jrxml_filepath) as h:
            jrxml_xml = h.read()
            self.assertEqual(self.STATIC_JRXML_FILE_WITHOUT_NAME2, jrxml_xml, 'jrxml file content does not match expected')
    
    def testViewRemoveInputControlFromMetadataFiles(self):
        mock_root = MagicMock(name='mock_root')
        mock_node1 = MagicMock(name='mock_node1')
        mock_node1.text.find.return_value = 0
        mock_node2 = MagicMock(name='mock_node2')
        mock_node1.getparent.return_value = mock_node2
        mock_node3 = etree.Element('mock_node3')
        mock_node3.text = 'Deleted Node'
        mock_node2.__getitem__.return_value = mock_node3
        mock_node4 = MagicMock(name='mock_node4')
        mock_node2.getparent.return_value = mock_node4
        node_list = [mock_node1]
        mock_root.xpath = MagicMock(side_effect=[node_list])
        self.report_action.removeInputControlFromMetadataFiles(root=mock_root, fieldname='name2', log=self.log)
        mock_node4.remove.assert_called_with(mock_node2)
        
    def testViewRemoveInputControlFromMetadata(self):
        field_name = 'name1'
        self.report_action.removeInputControlFromMetadata(metadata_filename=self.report_metadata_filepath, fieldname=field_name, log=self.log)
        with open(self.report_metadata_filepath) as h:
            report_metadata_xml = h.read()
            self.assertEqual(self.REPORT_METADATA_FILE_WITHOUT_NAME1, report_metadata_xml, 'Input control ' + field_name + ' not removed from metadata file or file corrupted')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
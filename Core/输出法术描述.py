import pandas as pd
import re
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
# ----------------- 初始化本地文件路径 -----------------
# 设置原始文件版本号
Version = "_11.0.2.55789"
# spell.csv 文件路径
Spell_path = os.path.join(current_dir, "..", "raw_datas", f"spell{Version}.csv")
# spellauraoptions.csv 文件路径
SpellAuraOptions_path = os.path.join(
    current_dir, "..", "raw_datas", f"spellauraoptions{Version}.csv"
)
# spellduration.csv 文件路径
SpellDuration_path = os.path.join(
    current_dir, "..", "raw_datas", f"spellduration{Version}.csv"
)
# spelleffect.csv 文件路径
SpellEffect_path = os.path.join(
    current_dir, "..", "raw_datas", f"spelleffect{Version}.csv"
)
# spellmisc.csv 文件路径
SpellMisc_path = os.path.join(current_dir, "..", "raw_datas", f"spellmisc{Version}.csv")
# spellname.csv 文件路径
SpellName_path = os.path.join(current_dir, "..", "raw_datas", f"spellname{Version}.csv")
# spellradius.csv 文件路径
SpellRadius_path = os.path.join(
    current_dir, "..", "raw_datas", f"spellradius{Version}.csv"
)
# ----------------------  END  -----------------------------

# ----------------- 初始化输入输出文件路径 -----------------
# spelllist.txt 文件路径   需要添加描述的法术id列表
SpellList_path = os.path.join(current_dir, "spelllist.txt")
# spelldesc.txt 文件路径   输出法术描述列表
SpellDesc_path = os.path.join(current_dir, "spelldesc.txt")
# ----------------------  END  -----------------------------


def load_data(
    spell_file: str = Spell_path,
    spellauraoptions_file: str = SpellAuraOptions_path,
    spellduration_file: str = SpellDuration_path,
    spelleffect_file: str = SpellEffect_path,
    spellmisc_file: str = SpellMisc_path,
    spellname_file: str = SpellName_path,
    spellradius_file: str = SpellRadius_path,
):
    spells_df = pd.read_csv(spell_file)
    spellauraoptions_df = pd.read_csv(spellauraoptions_file)
    spellduration_df = pd.read_csv(spellduration_file)
    spelleffect_df = pd.read_csv(spelleffect_file)
    spellmisc_df = pd.read_csv(spellmisc_file)
    spellname_df = pd.read_csv(spellname_file)
    spellradius_df = pd.read_csv(spellradius_file)

    return (
        spells_df,
        spellauraoptions_df,
        spellduration_df,
        spelleffect_df,
        spellmisc_df,
        spellname_df,
        spellradius_df,
    )


def format_number(value):
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def get_spell_description(
    spell_id,
    spells_df,
    spelleffect_df,
    spellmisc_df,
    spellduration_df,
    spellradius_df,
    spellname_df,
    spellauraoptions_df,
):
    spell_row = spells_df.loc[spells_df["ID"] == spell_id]
    if spell_row.empty:
        return f"Spell ID {spell_id} not found."

    description = spell_row.iloc[0]["Description_lang"]
    if pd.isna(description) or description.strip() == "":
        spell_name = get_spell_name(spell_id, spellname_df)
        return f"# {spell_name} (ID:{spell_id}): <此法术没有技能描述>"

    return process_description(
        description,
        spells_df,
        spelleffect_df,
        spellmisc_df,
        spellduration_df,
        spellradius_df,
        spellname_df,
        spellauraoptions_df,
        spell_id,
    )


def process_description(
    description,
    spells_df,
    spelleffect_df,
    spellmisc_df,
    spellduration_df,
    spellradius_df,
    spellname_df,
    spellauraoptions_df,
    parent_spell_id,
):
    pattern = re.compile(
        r"\$(?:(@spelldesc(\d+))|(@spellname(\d+))|"  # Matches $@spelldesc123 or $@spellname123
        r"(\?s(\d+))|(\?a(\d+))|"  # Matches $?s123 or $?a123
        r"(s(\d+))|((\d+)s(\d+))|"  # Matches $s123 or $1s123
        r"(d(\d*))|(\d+)d(\d*)|"  # Matches $d or $123d or $123d123
        r"(t(\d*))|(\d+)t(\d*)|"  # Matches $t or $123t or $123t123
        r"(A(\d*))|(\d+)A(\d*)|"  # Matches $A or $123A or $123A123
        r"(D(\d*))|(\d+)D(\d*)|"  # Matches $D or $123D or $123D123
        r"(a(\d*))|(\d+)a(\d*)|"  # Matches $a or $123a or $123a123
        r"(T(\d*))|(\d+)T(\d*)|"  # Matches $T or $123T or $123T123
        r"(u(\d*))|(\d+)u(\d*)|"  # Matches $u or $123u or $123u123
        r"(m(\d*))|(\d+)m(\d*))"  # Matches $m or $123m or $123m123
    )

    while "$" in description:
        matches = pattern.findall(description)
        if not matches:
            break
        for match in matches:
            (
                at_spelldesc,  # Matches @spelldesc123
                spell_desc_id,  # Captures the 123 from @spelldesc123
                at_spellname,  # Matches @spellname123
                spellname_id,  # Captures the 123 from @spellname123
                q_s,  # Matches $?s123
                q_s_id,  # Captures the 123 from $?s123
                q_a,  # Matches $?a123
                q_a_id,  # Captures the 123 from $?a123
                s_full,  # Matches $s123
                s_index,  # Captures the 123 from $s123
                digits_full,  # Matches $1s123
                spell_id,  # Captures the 1 from $1s123
                spell_index,  # Captures the 123 from $1s123
                d_full,  # Matches $d123
                d_index,  # Captures the 123 from $d123
                spell_d_id,  # Matches $123d123
                spell_d_index,  # Captures the 123 from $123d123
                t_full,  # Matches $t123
                t_index,  # Captures the 123 from $t123
                spell_t_id,  # Matches $123t123
                spell_t_index,  # Captures the 123 from $123t123
                a_full,  # Matches $A123
                a_index,  # Captures the 123 from $A123
                spell_a_id,  # Matches $123A123
                spell_a_index,  # Captures the 123 from $123A123
                D_full,  # Matches $D123
                D_index,  # Captures the 123 from $D123
                spell_D_id,  # Matches $123D123
                spell_D_index,  # Captures the 123 from $123D123
                a_lower_full,  # Matches $a123
                a_lower_index,  # Captures the 123 from $a123
                spell_a_lower_id,  # Matches $123a123
                spell_a_lower_index,  # Captures the 123 from $123a123
                T_full,  # Matches $T123
                T_index,  # Captures the 123 from $T123
                spell_T_id,  # Matches $123T123
                spell_T_index,  # Captures the 123 from $123T123
                u_full,  # Matches $u123
                u_index,  # Captures the 123 from $u123
                spell_u_id,  # Matches $123u123
                spell_u_index,  # Captures the 123 from $123u123
                m_full,  # Matches $m123
                m_index,  # Captures the 123 from $m123
                spell_m_id,  # Matches $123m123
                spell_m_index,  # Captures the 123 from $123m123
            ) = match

            if at_spelldesc:
                spell_id = int(spell_desc_id)
                replacement = get_spell_description(
                    spell_id,
                    spells_df,
                    spelleffect_df,
                    spellmisc_df,
                    spellduration_df,
                    spellradius_df,
                    spellname_df,
                    spellauraoptions_df,
                )
                description = description.replace(
                    f"$@spelldesc{spell_id}", replacement, 1
                )
            elif at_spellname:
                spell_id = int(spellname_id)
                replacement = get_spell_name(spell_id, spellname_df)
                description = description.replace(
                    f"$@spellname{spell_id}", replacement, 1
                )
            elif q_s:
                spell_id = int(q_s_id)
                replacement = get_spell_name(spell_id, spellname_df, " 天赋")
                description = description.replace(f"$?s{spell_id}", replacement, 1)
            elif q_a:
                spell_id = int(q_a_id)
                replacement = get_spell_name(spell_id, spellname_df, " 天赋")
                description = description.replace(f"$?a{spell_id}", replacement, 1)
            elif s_full:
                index = int(s_index) - 1
                replacement = get_spelleffect_value(
                    parent_spell_id, index, spelleffect_df
                )
                description = description.replace(f"$s{s_index}", replacement, 1)
            elif digits_full:
                spell_id = int(spell_id)
                index = int(spell_index) - 1
                replacement = get_spelleffect_value(spell_id, index, spelleffect_df)
                description = description.replace(
                    f"${spell_id}s{spell_index}", replacement, 1
                )
            elif d_full:
                index = int(d_index) - 1 if d_index else 0
                replacement = get_spellduration_value(
                    parent_spell_id, index, spellmisc_df, spellduration_df
                )
                description = description.replace(f"$d{d_index}", replacement, 1)
            elif spell_d_id:
                spell_id = int(spell_d_id)
                index = int(spell_d_index) - 1 if spell_d_index else 0
                replacement = get_spellduration_value(
                    spell_id, index, spellmisc_df, spellduration_df
                )
                description = description.replace(
                    f"${spell_d_id}d{spell_d_index}", replacement, 1
                )
            elif D_full:
                index = int(D_index) - 1 if D_index else 0
                replacement = get_spellduration_value(
                    parent_spell_id, index, spellmisc_df, spellduration_df
                )
                description = description.replace(f"$D{D_index}", replacement, 1)
            elif spell_D_id:
                spell_id = int(spell_D_id)
                index = int(spell_D_index) - 1 if spell_D_index else 0
                replacement = get_spellduration_value(
                    spell_id, index, spellmisc_df, spellduration_df
                )
                description = description.replace(
                    f"${spell_D_id}D{spell_D_index}", replacement, 1
                )
            elif t_full:
                index = int(t_index) - 1 if t_index else 0
                replacement = get_effect_aura_period(
                    parent_spell_id, index, spelleffect_df
                )
                description = description.replace(f"$t{t_index}", replacement, 1)
            elif spell_t_id:
                spell_id = int(spell_t_id)
                index = int(spell_t_index) - 1 if spell_t_index else 0
                replacement = get_effect_aura_period(spell_id, index, spelleffect_df)
                description = description.replace(
                    f"${spell_t_id}t{spell_t_index}", replacement, 1
                )
            elif T_full:
                index = int(T_index) - 1 if T_index else 0
                replacement = get_effect_aura_period(
                    parent_spell_id, index, spelleffect_df
                )
                description = description.replace(f"$T{T_index}", replacement, 1)
            elif spell_T_id:
                spell_id = int(spell_T_id)
                index = int(spell_T_index) - 1 if spell_T_index else 0
                replacement = get_effect_aura_period(spell_id, index, spelleffect_df)
                description = description.replace(
                    f"${spell_T_id}T{spell_T_index}", replacement, 1
                )
            elif a_full:
                index = int(a_index) - 1 if a_index else 0
                replacement = get_effect_radius(
                    parent_spell_id, index, spelleffect_df, spellradius_df
                )
                description = description.replace(f"$A{a_index}", replacement, 1)
            elif spell_a_id:
                spell_id = int(spell_a_id)
                index = int(spell_a_index) - 1 if spell_a_index else 0
                replacement = get_effect_radius(
                    spell_id, index, spelleffect_df, spellradius_df
                )
                description = description.replace(
                    f"${spell_a_id}A{spell_a_index}", replacement, 1
                )
            elif a_lower_full:
                index = int(a_lower_index) - 1 if a_lower_index else 0
                replacement = get_effect_radius(
                    parent_spell_id, index, spelleffect_df, spellradius_df
                )
                description = description.replace(f"$a{a_lower_index}", replacement, 1)
            elif spell_a_lower_id:
                spell_id = int(spell_a_lower_id)
                index = int(spell_a_lower_index) - 1 if spell_a_lower_index else 0
                replacement = get_effect_radius(
                    spell_id, index, spelleffect_df, spellradius_df
                )
                description = description.replace(
                    f"${spell_a_lower_id}a{spell_a_lower_index}", replacement, 1
                )
            elif u_full:
                index = int(u_index) - 1 if u_index else 0
                replacement = get_cumulative_aura(
                    parent_spell_id, index, spellauraoptions_df
                )
                description = description.replace(f"$u{u_index}", replacement, 1)
            elif spell_u_id:
                spell_id = int(spell_u_id)
                index = int(spell_u_index) - 1 if spell_u_index else 0
                replacement = get_cumulative_aura(spell_id, index, spellauraoptions_df)
                description = description.replace(
                    f"${spell_u_id}u{spell_u_index}", replacement, 1
                )
            elif m_full:
                index = int(m_index) - 1 if m_index else 0
                replacement = get_effect_base_points(
                    parent_spell_id, index, spelleffect_df
                )
                description = description.replace(f"$m{m_index}", replacement, 1)
            elif spell_m_id:
                spell_id = int(spell_m_id)
                index = int(spell_m_index) - 1 if spell_m_index else 0
                replacement = get_effect_base_points(spell_id, index, spelleffect_df)
                description = description.replace(
                    f"${spell_m_id}m{spell_m_index}", replacement, 1
                )
            else:
                description = description.replace(f"${match[0]}", f"#{match[0]}", 1)

    # Process any remaining ${} expressions
    eval_pattern = re.compile(r"\$\{([^}]+)\}")
    eval_matches = eval_pattern.findall(description)
    for eval_match in eval_matches:
        try:
            if (
                re.search("[a-zA-Z]", eval_match) is None
            ):  # Only process if no letters are present
                evaluated_value = eval(eval_match)
                description = description.replace(
                    f"${{{eval_match}}}", str(evaluated_value)
                )
        except Exception as e:
            continue

    return description


def get_cumulative_aura(spell_id, index, spellauraoptions_df):
    aura_row = spellauraoptions_df.loc[spellauraoptions_df["SpellID"] == spell_id]
    if aura_row.empty:
        return "Cumulative Aura not found."
    return str(aura_row.iloc[0]["CumulativeAura"])


def get_spell_name(spell_id, spellname_df, suffix=""):
    spell_row = spellname_df.loc[spellname_df["ID"] == spell_id]
    if spell_row.empty:
        return "Spell name not found."
    return f"{spell_row.iloc[0]['Name_lang']}{suffix}"


def get_spelleffect_value(spell_id, index, spelleffect_df):
    effect_row = spelleffect_df.loc[
        (spelleffect_df["SpellID"] == spell_id)
        & (spelleffect_df["EffectIndex"] == index)
    ]
    if effect_row.empty:
        return "Effect not found."

    effect_row = effect_row.iloc[0]
    effect_type = effect_row["Effect"]

    if effect_type == 10:
        coefficient = effect_row["EffectBonusCoefficient"]
        return f"({format_number(coefficient * 100)}% 法术强度)"
    elif effect_type == 2:
        coefficient_from_ap = effect_row["BonusCoefficientFromAP"]
        if coefficient_from_ap != 0:
            return f"({format_number(coefficient_from_ap * 100)}% 攻击强度)"
        else:
            coefficient = effect_row["EffectBonusCoefficient"]
            if coefficient != 0:
                return f"({format_number(coefficient * 100)}% 法术强度)"
            else:
                base_points = effect_row["EffectBasePointsF"]
                return format_number(base_points)
    else:
        return format_number(effect_row["EffectBasePointsF"])


def get_spellduration_value(spell_id, index, spellmisc_df, spellduration_df):
    misc_row = spellmisc_df.loc[spellmisc_df["SpellID"] == spell_id]
    if misc_row.empty:
        return "Duration not found."

    duration_index = misc_row.iloc[0]["DurationIndex"]
    duration_row = spellduration_df.loc[spellduration_df["ID"] == duration_index]
    if duration_row.empty:
        return "Duration not found."

    duration_value = duration_row.iloc[0]["Duration"]
    return format_number(duration_value * 0.001) + "秒"


def get_effect_aura_period(spell_id, index, spelleffect_df):
    effect_row = spelleffect_df.loc[
        (spelleffect_df["SpellID"] == spell_id)
        & (spelleffect_df["EffectIndex"] == index)
    ]
    if effect_row.empty:
        return "Period not found."

    effect_row = effect_row.iloc[0]
    aura_period = effect_row["EffectAuraPeriod"]
    return format_number(aura_period * 0.001)


def get_effect_radius(spell_id, index, spelleffect_df, spellradius_df):
    effect_row = spelleffect_df.loc[
        (spelleffect_df["SpellID"] == spell_id)
        & (spelleffect_df["EffectIndex"] == index)
    ]
    if effect_row.empty:
        return "Radius not found."

    effect_row = effect_row.iloc[0]
    radius_index = effect_row["EffectRadiusIndex[0]"]
    if radius_index == 0:
        radius_index = effect_row["EffectRadiusIndex[1]"]

    radius_row = spellradius_df.loc[spellradius_df["ID"] == radius_index]
    if radius_row.empty:
        return "Radius not found."

    radius_value = radius_row.iloc[0]["Radius"]
    return format_number(radius_value)


def get_effect_base_points(spell_id, index, spelleffect_df):
    effect_row = spelleffect_df.loc[
        (spelleffect_df["SpellID"] == spell_id)
        & (spelleffect_df["EffectIndex"] == index)
    ]
    if effect_row.empty:
        return "Effect base points not found."

    base_points = effect_row.iloc[0]["EffectBasePointsF"]
    return format_number(base_points / 1000)


def main():
    (
        spells_df,
        spellauraoptions_df,
        spellduration_df,
        spelleffect_df,
        spellmisc_df,
        spellname_df,
        spellradius_df,
    ) = load_data()

    with open(SpellList_path, "r", encoding="utf-8") as file:
        spell_ids = [line.strip() for line in file.readlines()]

    total_spells = len(spell_ids)
    results = []
    for i, spell_id in enumerate(spell_ids, 1):
        spell_id = int(
            spell_id.strip().replace(",", "")
        )  # Remove any extra commas or spaces
        try:
            description = get_spell_description(
                spell_id,
                spells_df,
                spelleffect_df,
                spellmisc_df,
                spellduration_df,
                spellradius_df,
                spellname_df,
                spellauraoptions_df,
            )
            spell_name = get_spell_name(spell_id, spellname_df)
            results.append(f"# {spell_name} (ID:{spell_id}): {description}")
        except Exception as e:
            results.append(f"Error processing Spell ID {spell_id}: {e}")
        if i % max(1, (total_spells // 50)) == 0:  # 每2%输出一次进度
            print(f"Processing progress: {i / total_spells * 100:.2f}%")

    with open(SpellDesc_path, "w", encoding="utf-8") as file:
        for result in results:
            file.write(result.replace("\n", " ") + "\n")


if __name__ == "__main__":
    main()

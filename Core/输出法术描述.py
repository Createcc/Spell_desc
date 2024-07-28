import pandas as pd
import re
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
# ----------------- 初始化本地文件路径 -----------------
# spell.csv 文件路径
Spell_path = os.path.join(current_dir, "..", "raw_datas", "spell.csv")
# spellauraoptions.csv 文件路径
SpellAuraOptions_path = os.path.join(
    current_dir, "..", "raw_datas", "spellauraoptions.csv"
)
# spellduration.csv 文件路径
SpellDuration_path = os.path.join(current_dir, "..", "raw_datas", "spellduration.csv")
# spelleffect.csv 文件路径
SpellEffect_path = os.path.join(current_dir, "..", "raw_datas", "spelleffect.csv")
# spellmisc.csv 文件路径
SpellMisc_path = os.path.join(current_dir, "..", "raw_datas", "spellmisc.csv")
# spellname.csv 文件路径
SpellName_path = os.path.join(current_dir, "..", "raw_datas", "spellname.csv")
# spellradius.csv 文件路径
SpellRadius_path = os.path.join(current_dir, "..", "raw_datas", "spellradius.csv")
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
        r"\$(?:(@spelldesc(\d+))|(@spellname(\d+))|(\?s(\d+))|(\?a(\d+))|"
        r"(s(\d+))|((\d+)s(\d+))|"
        r"(d(\d*))|(\d+)d(\d*)|"
        r"(t(\d*))|(\d+)t(\d*)|"
        r"(A(\d*))|(\d+)A(\d*)|"
        r"(D(\d*))|(\d+)D(\d*)|"
        r"(a(\d*))|(\d+)a(\d*)|"
        r"(T(\d*))|(\d+)T(\d*)|"
        r"(u(\d*))|(\d+)u(\d*)|"
        r"(m(\d*))|(\d+)m(\d*))"
    )

    while "$" in description:
        matches = pattern.findall(description)
        if not matches:
            break
        for match in matches:
            (
                at_spelldesc,
                spell_desc_id,
                at_spellname,
                spellname_id,
                q_s,
                q_s_id,
                q_a,
                q_a_id,
                s_full,
                s_index,
                digits_full,
                spell_id,
                spell_index,
                d_full,
                d_index,
                spell_d_id,
                spell_d_index,
                t_full,
                t_index,
                spell_t_id,
                spell_t_index,
                a_full,
                a_index,
                spell_a_id,
                spell_a_index,
                D_full,
                D_index,
                spell_D_id,
                spell_D_index,
                a_lower_full,
                a_lower_index,
                spell_a_lower_id,
                spell_a_lower_index,
                T_full,
                T_index,
                spell_T_id,
                spell_T_index,
                u_full,
                u_index,
                spell_u_id,
                spell_u_index,
                m_full,
                m_index,
                spell_m_id,
                spell_m_index,
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

    with open("SPELLLIST.TXT", "r", encoding="utf-8") as file:
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

    with open("SPELLDESC.TXT", "w", encoding="utf-8") as file:
        for result in results:
            file.write(result.replace("\n", " ") + "\n")


if __name__ == "__main__":
    main()

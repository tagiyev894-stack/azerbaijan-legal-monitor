def one_line_summary(title):
    """Başlıqdan bir cümləlik analiz çıxarır."""
    t = title.lower()
    # 1. Dəyişikliklər
    if "dəyişiklik" in t:
        # Konkret sahəni tapmağa çalış
        if "vergi" in t:
            return "Vergi Məcəlləsinə dəyişiklik edilir."
        if "əmək" in t:
            return "Əmək Məcəlləsinə dəyişiklik edilir."
        if "inzibati" in t or "xətalar" in t:
            return "İnzibati Xətalar Məcəlləsinə dəyişiklik edilir."
        if "cinayət" in t:
            return "Cinayət Məcəlləsinə dəyişiklik edilir."
        if "mülki" in t:
            return "Mülki Məcəlləyə dəyişiklik edilir."
        if "təhsil" in t:
            return "Təhsil sahəsində normativ dəyişiklik."
        return "Müxtəlif normativ hüquqi aktlara dəyişiklik edilir."

    # 2. Təsdiqlər
    if "təsdiq" in t:
        if "qayda" in t:
            return "Yeni qaydalar təsdiq edilir."
        if "proqram" in t or "strategiya" in t:
            return "Dövlət proqramı/strategiyası təsdiq edilir."
        if "əsasnamə" in t or "nizamnamə" in t:
            return "Əsasnamə/Nizamnamə təsdiq edilir."
        return "Sənəd təsdiq edilir."

    # 3. Ləğvlər
    if "ləğv" in t:
        return "Mövcud normativ akt ləğv edilir."

    # 4. Yeni yaradılma
    if "yaradılması" in t or "təşkil" in t:
        if "komissiya" in t:
            return "Yeni komissiya yaradılır."
        if "idarə" in t or "agentlik" in t:
            return "Yeni dövlət qurumu yaradılır."
        return "Yeni qurum/struktur yaradılır."

    # 5. Sosial məsələlər
    if "müavinət" in t or "pensiya" in t:
        return "Sosial ödənişlərlə bağlı tənzimləmə."
    if "güzəşt" in t:
        return "Güzəşt/vergi azadolmaları ilə bağlı qərar."

    # 6. Fallback
    if "qərar" in t:
        return "Nazirlər Kabineti tərəfindən qərar qəbul edilmişdir."
    if "sərəncam" in t:
        return "Prezident sərəncamı imzalanmışdır."
    if "fərman" in t:
        return "Prezident fərmanı imzalanmışdır."
    if "qanun" in t:
        return "Yeni qanun qəbul edilmişdir."

    return "Yeni normativ akt."

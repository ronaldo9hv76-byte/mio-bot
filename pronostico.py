def generate_tilt_payload():
    # Caratteri che forzano il ricalcolo dei glifi e della direzione
    # Usiamo un mix di RLO (Right-to-Left) e Jamo (Hangul) che sono pesantissimi
    heavy_chars = ["\u202e", "\u202d", "\u1160", "\u3164", "\u2067", "\u2068"]
    
    # Prefisso corto per lasciare spazio al payload
    prefix = "⚠️ [SYS_ERR] " 
    
    # TikTok permette circa 150 caratteri. Noi ne usiamo 140 per sicurezza.
    max_len = 140 - len(prefix)
    
    payload = prefix + "".join(random.choice(heavy_chars) for _ in range(max_len))
    return payload

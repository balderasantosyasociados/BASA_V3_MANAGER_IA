def calculate_forensic_isr(gross_salary: float, tss_deducted: float, is_salary_13: bool = False) -> float:
    if is_salary_13:
        return 0.0
    
    # La base imponible es el salario bruto menos la retención de TSS
    taxable_base_monthly = gross_salary - tss_deducted
    taxable_base_annual = taxable_base_monthly * 12
    
    # Escala Anual DGII vigente (Desde 2017 a la actualidad)
    EXEMPT_LIMIT = 416220.00
    SCALE_1_LIMIT = 624329.00
    SCALE_2_LIMIT = 867123.00
    
    annual_isr = 0.0
    
    if taxable_base_annual <= EXEMPT_LIMIT:
        annual_isr = 0.0
    elif taxable_base_annual <= SCALE_1_LIMIT:
        annual_isr = (taxable_base_annual - EXEMPT_LIMIT) * 0.15
    elif taxable_base_annual <= SCALE_2_LIMIT:
        fixed_rate_1 = 31216.00
        annual_isr = fixed_rate_1 + ((taxable_base_annual - SCALE_1_LIMIT) * 0.20)
    else:
        fixed_rate_2 = 79776.00
        annual_isr = fixed_rate_2 + ((taxable_base_annual - SCALE_2_LIMIT) * 0.25)
        
    return round(annual_isr / 12, 2)

import math

# Variáveis de entrada
DailyGHImonth = {
    "January": 5.604,
    "February": 5.753,
    "March": 5.085,
    "April": 4.615,
    "May": 3.793,
    "June": 3.535,
    "July": 3.705,
    "August": 4.612,
    "September": 4.836,
    "October": 5.484,
    "November": 5.678,
    "December": 6.121,
}

Tilt = 20
Azimuth = 347
Lat = -22.89
Long = -47.02
Pfv = 1
YearofInstallation = 2025
PR = 0.75
Degradation = 0.007

# Dias médios de cada mês
averageDayOfMonth = {
    "January": 15,
    "February": 45,
    "March": 74,
    "April": 105,
    "May": 135,
    "June": 166,
    "July": 196,
    "August": 227,
    "September": 258,
    "October": 288,
    "November": 319,
    "December": 349
}

# Número de dias em cada mês (sem considerar anos bissextos)
numberOfDays = {
    "January": 31,
    "February": 28,
    "March": 31,
    "April": 30,
    "May": 31,
    "June": 30,
    "July": 31,
    "August": 31,
    "September": 30,
    "October": 31,
    "November": 30,
    "December": 31
}

# Função para calcular a declinação solar para o dia médio do mês usando o modelo Sandia
def calculateSolarDeclination(dayOfYear):
    declination = 23.45 * math.sin(math.radians((360 * ((dayOfYear + 284) / 365))))
    return declination

# Função para calcular o ângulo zenital solar 
def calculateSolarZenithAngle(declination, lat):

    solarHourAngle = math.degrees(math.acos(-math.tan(math.radians(lat)) * math.tan(math.radians(declination))))

    solarZenithAngle = math.degrees(math.acos(math.sin(math.radians(lat)) * math.sin(math.radians(declination)) + math.cos(math.radians(lat)) * math.cos(math.radians(declination)) * math.cos(math.radians(0))))

    return solarZenithAngle

# Função para calcular a irradiância horizontal difusa (DHI) usando o modelo de Reindl
def calculateDHI(GHI, solarZenithAngle, dayOfYear, lat, declination):

    extraterrestrialRadiation = 1367 * (1 + 0.033 * math.cos(math.radians((360 * dayOfYear) / 365)))

    sunriseHourAngle = -math.degrees(math.acos(-math.tan(math.radians(lat)) * math.tan(math.radians(declination))))

    sunsetHourAngle = math.degrees(math.acos(-math.tan(math.radians(lat)) * math.tan(math.radians(declination))))
    
    #dailyExtraterrestrialRadiation = (24 / (math.pi * 1000000)) * 3600 * extraterrestrialRadiation * (math.cos(math.radians(lat)) * math.cos(math.radians(declination)) * math.sin(math.radians(sunsetHourAngle)) + ((math.pi * sunsetHourAngle) / 180) * math.sin(math.radians(lat)) * math.sin(math.radians(declination)))

    dailyExtraterrestrialRadiation = (12 / (math.pi * 1000000)) * 3600 * extraterrestrialRadiation * (math.cos(math.radians(lat)) * math.cos(math.radians(declination)) * (math.sin(math.radians(sunsetHourAngle))-math.sin(math.radians(sunriseHourAngle))) + ((math.pi * (sunsetHourAngle - sunriseHourAngle) / 180)) * math.sin(math.radians(lat)) * math.sin(math.radians(declination)))
    
    # Modelo de Reindl
    Kt = ((GHI * 3.6)/(dailyExtraterrestrialRadiation))
    
    if Kt <= 0.03:
        Kd = (1.02 - (0.248 * Kt))
    elif Kt <= 0.78:
        Kd = (1.45 - (1.67 * Kt))
    else:
        Kd = (0.147)
    
    DHI = Kd * GHI
    
    return DHI, Kt, Kd, sunsetHourAngle, dailyExtraterrestrialRadiation

# Função para calcular a irradiância direta normal (DNI)
def calculateDNI(GHI, DHI, solarZenithAngle):
    DNI = (GHI - DHI) / math.cos(math.radians(solarZenithAngle))
    return DNI

# Função para calcular a irradiância no plano inclinado usando o modelo Sandia
def calculatePOA(GHI, DHI, DNI, declination, solarZenithAngle, tilt, azimuth, lat, long, dayOfYear, Kt, Kd):
    
    # Constantes do modelo Sandia
    albedo = 0.2 # Refletância do solo

    # Cálculo do ângulo de incidência conforme o modelo da Homer Energy
    incidenceAngle = math.degrees(math.acos(
        math.sin(math.radians(declination)) * math.sin(math.radians(lat)) * math.cos(math.radians(tilt)) -
        math.sin(math.radians(declination)) * math.cos(math.radians(lat)) * math.sin(math.radians(tilt)) * math.cos(math.radians(azimuth+180)) +
        math.cos(math.radians(declination)) * math.cos(math.radians(lat)) * math.cos(math.radians(tilt)) * math.cos(math.radians(0)) +  
        math.cos(math.radians(declination)) * math.sin(math.radians(lat)) * math.sin(math.radians(tilt)) * math.cos(math.radians(azimuth+180)) *
        math.cos(math.radians(0)) + 
        math.cos(math.radians(declination)) * math.sin(math.radians(tilt)) *
        math.sin(math.radians(azimuth+180))*math.sin(math.radians(0))))

    # Verificação de limites para o ângulo de incidência
    cosIncidenceAngle = max(0, min(1, math.cos(math.radians(incidenceAngle))))

    # Componentes da irradiância 
    directPOAIrradiance = DNI * cosIncidenceAngle
    
    # Cálculo da radiação difusa no plano inclinado usando o modelo Sandia
    diffusePOAIrradiance = DHI * ((1 + math.cos(math.radians(tilt))) / 2)
    reflectedPOAIrradiance = GHI * albedo * ((1 - math.cos(math.radians(tilt))) / 2)

    # Irradiância total no plano inclinado
    POA = directPOAIrradiance + diffusePOAIrradiance + reflectedPOAIrradiance
    
    # Retornar todas as variáveis calculadas para análise
    return {
        'declination': declination,
        'solarZenithAngle': solarZenithAngle,
        'dailyExtraterrestrialRadiation': dailyExtraterrestrialRadiation,
        'sunsetHourAngle': sunsetHourAngle,
        'Kt': Kt,
        'Kd': Kd,
        'GHI': GHI,
        'DNI': DNI,
        'DHI': DHI,
        'incidenceAngle': incidenceAngle,
        'POA': POA
    }

# Calcular a irradiância para cada mês e armazenar todas as variáveis calculadas
calculated_variables_monthly = {}
for month in DailyGHImonth:
    dayOfYear = averageDayOfMonth[month]
    declination = calculateSolarDeclination(dayOfYear)
    solarZenithAngle = calculateSolarZenithAngle(declination, Lat)
    GHI = DailyGHImonth[month]
    DHI, Kt, Kd, sunsetHourAngle, dailyExtraterrestrialRadiation = calculateDHI(GHI, solarZenithAngle, dayOfYear, Lat, declination)
    DNI = calculateDNI(GHI, DHI, solarZenithAngle)
    calculated_variables_monthly[month] = calculatePOA(GHI, DHI, DNI, declination, solarZenithAngle, Tilt, Azimuth, Lat, Long, dayOfYear, Kt, Kd)

# Calcular a geração de energia para cada mês
ThisYear = 2025
MonthlyGeneration = {}
for month in DailyGHImonth:
    POA = calculated_variables_monthly[month]['POA']
    MonthlyGeneration[month] = Pfv * POA * numberOfDays[month] * PR * (1 - Degradation * (ThisYear - YearofInstallation))

print("\nVariáveis Calculadas Mensalmente:")
for month in calculated_variables_monthly:
    print(calculated_variables_monthly[month])

print("\nPOA Mensal:")
for month in calculated_variables_monthly:
    print(f"{calculated_variables_monthly[month]['POA']:.2f}")

print("\nGeração de Energia Mensal (kWh):")
for month in DailyGHImonth:
    print(f"{MonthlyGeneration[month]:.0f}")
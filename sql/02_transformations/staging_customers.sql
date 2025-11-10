-- STAGING: CUSTOMERS

-- Camada de staging para clientes com limpeza e enriquecimento
-- Estilo dbt - fonte → staging → marts
-- Autor: Andre Bomfim
-- Data: Outubro 2025

-- STG_CUSTOMERS: Clientes limpos e enriquecidos
CREATE OR REPLACE TABLE `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers` AS

WITH source AS (
  SELECT * 
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.customers`
),

cleaned AS (
  SELECT 
    -- Primary keys
    customer_id,
    customer_unique_id,
    
    -- Geographic info (limpo e padronizado)
    LPAD(customer_zip_code_prefix, 5, '0') AS customer_zip_code_prefix,
    UPPER(TRIM(customer_city)) AS customer_city,
    UPPER(TRIM(customer_state)) AS customer_state,
    
    -- Metadata
    CURRENT_TIMESTAMP() AS _loaded_at
    
  FROM source
  WHERE customer_id IS NOT NULL
),

enriched AS (
  SELECT 
    *,
    
    -- ENRICHMENT: Categorização geográfica
    
    -- Região do Brasil
    CASE 
      WHEN customer_state IN ('AC', 'AP', 'AM', 'PA', 'RO', 'RR', 'TO') THEN 'Norte'
      WHEN customer_state IN ('AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'Nordeste'
      WHEN customer_state IN ('DF', 'GO', 'MT', 'MS') THEN 'Centro-Oeste'
      WHEN customer_state IN ('ES', 'MG', 'RJ', 'SP') THEN 'Sudeste'
      WHEN customer_state IN ('PR', 'RS', 'SC') THEN 'Sul'
      ELSE 'Unknown'
    END AS customer_region,
    
    -- Capital ou Interior
    CASE 
      WHEN customer_city IN (
        'RIO BRANCO', 'MACAPA', 'MANAUS', 'BELEM', 'PORTO VELHO', 'BOA VISTA', 'PALMAS',
        'MACEIO', 'SALVADOR', 'FORTALEZA', 'SAO LUIS', 'JOAO PESSOA', 'RECIFE', 'TERESINA', 'NATAL', 'ARACAJU',
        'BRASILIA', 'GOIANIA', 'CUIABA', 'CAMPO GRANDE',
        'VITORIA', 'BELO HORIZONTE', 'RIO DE JANEIRO', 'SAO PAULO',
        'CURITIBA', 'PORTO ALEGRE', 'FLORIANOPOLIS'
      ) THEN 'Capital'
      ELSE 'Interior'
    END AS customer_location_type,
    
    -- Principais áreas metropolitanas
    CASE 
      WHEN customer_city IN ('SAO PAULO', 'GUARULHOS', 'OSASCO', 'SAO BERNARDO DO CAMPO', 'SANTO ANDRE', 'SAO CAETANO DO SUL', 'DIADEMA', 'MAUA', 'MOGI DAS CRUZES', 'BARUERI', 'COTIA', 'FERRAZ DE VASCONCELOS', 'FRANCISCO MORATO', 'FRANCO DA ROCHA', 'ITAPECERICA DA SERRA', 'ITAPEVI', 'ITAQUAQUECETUBA', 'JANDIRA', 'JUQUITIBA', 'MAIRIPORA', 'POA', 'RIBEIRAO PIRES', 'RIO GRANDE DA SERRA', 'SALESOPOLIS', 'SANTA ISABEL', 'SANTANA DE PARNAIBA', 'SUZANO', 'TABOAO DA SERRA', 'VARGEM GRANDE PAULISTA') 
        THEN 'São Paulo Metro'
      WHEN customer_city IN ('RIO DE JANEIRO', 'NITEROI', 'SAO GONCALO', 'DUQUE DE CAXIAS', 'NOVA IGUACU', 'BELFORD ROXO', 'MESQUITA', 'NILOPOLIS', 'QUEIMADOS', 'SAO JOAO DE MERITI', 'ITABORAI', 'JAPERI', 'MAGE', 'PARACAMBI', 'PETROPOLIS', 'SEROPEDICA', 'TANGUA', 'MARICA', 'GUAPIMIRIM', 'CACHOEIRAS DE MACACU', 'RIO BONITO') 
        THEN 'Rio de Janeiro Metro'
      WHEN customer_city IN ('BELO HORIZONTE', 'CONTAGEM', 'BETIM', 'NOVA LIMA', 'RIBEIRAO DAS NEVES', 'SANTA LUZIA', 'SABARA', 'VESPASIANO', 'PEDRO LEOPOLDO', 'LAGOA SANTA', 'IBIRITE', 'SETE LAGOAS', 'PARA DE MINAS', 'BRUMADINHO', 'FLORESTAL', 'JUATUBA', 'SAO JOAQUIM DE BICAS', 'ESMERALDAS', 'IGARAPE', 'CONFINS', 'MATEUS LEME', 'RIO ACIMA', 'RAPOSOS', 'NOVA UNIAO', 'ITATIAIUCU', 'ITAGUARA', 'ITABIRITO', 'CRUCILÂNDIA', 'RIO MANSO', 'BONFIM', 'FORTUNA DE MINAS', 'FUNILÂNDIA', 'INHAUMA', 'JABOTICATUBAS', 'MATOZINHOS', 'CAPIM BRANCO', 'BARAO DE COCAIS', 'CAETE', 'MARIO CAMPOS', 'SARZEDO', 'TAQUARACU DE MINAS') 
        THEN 'Belo Horizonte Metro'
      WHEN customer_city IN ('CURITIBA', 'SAO JOSE DOS PINHAIS', 'COLOMBO', 'PINHAIS', 'ARAUCARIA', 'FAZENDA RIO GRANDE', 'CAMPO LARGO', 'ALMIRANTE TAMANDARE', 'CAMPO MAGRO', 'PIRAQUARA', 'QUATRO BARRAS', 'BALSA NOVA', 'BOCAIUVA DO SUL', 'CAMPINA GRANDE DO SUL', 'CERRO AZUL', 'CONTENDA', 'DOUTOR ULYSSES', 'ITAPERUCU', 'MANDIRITUBA', 'QUITANDINHA', 'RIO BRANCO DO SUL', 'TIJUCAS DO SUL', 'TUNAS DO PARANA', 'AGUDOS DO SUL', 'ADRIANOPOLIS', 'ANTONINA', 'GUARATUBA', 'LAPA', 'MORRETES', 'PARANAGUA') 
        THEN 'Curitiba Metro'
      WHEN customer_city IN ('PORTO ALEGRE', 'CANOAS', 'GRAVATAI', 'VIAMAO', 'SAO LEOPOLDO', 'NOVO HAMBURGO', 'SAPUCAIA DO SUL', 'CACHOEIRINHA', 'ALVORADA', 'GUAIBA', 'ELDORADO DO SUL', 'GLORINHA', 'IVOTI', 'NOVA SANTA RITA', 'PORTAO', 'PRESIDENTE LUCENA', 'SANTO ANTONIO DA PATRULHA', 'TRIUNFO', 'CAMPO BOM', 'DOIS IRMAOS', 'ESTANCIA VELHA', 'ESTEIO', 'NOVA HARTZ', 'PAROBÉ', 'SAPIRANGA', 'ARARICA', 'CAPELA DE SANTANA', 'CHARQUEADAS', 'GENERAL CÂMARA', 'ARROIO DOS RATOS', 'BARAO DO TRIUNFO', 'MINAS DO LEAO', 'MARIANA PIMENTEL', 'SAO JERONIMO', 'TAPES', 'BARRA DO RIBEIRO') 
        THEN 'Porto Alegre Metro'
      ELSE 'Other'
    END AS customer_metro_area,
    
    
    -- ENRICHMENT: Flags e categorias
    
    -- Estado econômico (PIB per capita aproximado)
    CASE 
      WHEN customer_state IN ('SP', 'RJ', 'DF', 'SC', 'RS') THEN 'High GDP'
      WHEN customer_state IN ('PR', 'ES', 'MG', 'MT', 'MS', 'GO') THEN 'Medium GDP'
      ELSE 'Lower GDP'
    END AS state_gdp_tier,
    
    -- Populacao do estado (faixas)
    CASE 
      WHEN customer_state = 'SP' THEN 'Very High (40M+)'
      WHEN customer_state IN ('MG', 'RJ', 'BA') THEN 'High (10M-20M)'
      WHEN customer_state IN ('RS', 'PR', 'PE', 'CE') THEN 'Medium (5M-10M)'
      ELSE 'Lower (<5M)'
    END AS state_population_tier,
    
    -- Distância do centro econômico (São Paulo) - simplificado
    CASE 
      WHEN customer_state = 'SP' THEN 'Very Close'
      WHEN customer_state IN ('RJ', 'MG', 'PR', 'SC', 'MS') THEN 'Close'
      WHEN customer_state IN ('RS', 'ES', 'GO', 'MT', 'DF') THEN 'Medium'
      WHEN customer_state IN ('BA', 'SE', 'AL', 'PE', 'PB', 'RN', 'CE') THEN 'Far'
      ELSE 'Very Far'
    END AS distance_from_sp,
    
    -- Validação de CEP
    CASE 
      WHEN LENGTH(customer_zip_code_prefix) = 5 THEN TRUE
      ELSE FALSE
    END AS is_valid_zipcode

  FROM cleaned
),


-- CUSTOMER DEDUPLICATION (customer_unique_id)
customer_master AS (
  SELECT 
    customer_unique_id,
    
    -- Pegar a localização mais recente (assumindo que customer_id mais recente é mais atual)
    MAX(customer_state) AS customer_state,
    MAX(customer_city) AS customer_city,
    MAX(customer_zip_code_prefix) AS customer_zip_code_prefix,
    MAX(customer_region) AS customer_region,
    MAX(customer_location_type) AS customer_location_type,
    MAX(customer_metro_area) AS customer_metro_area,
    MAX(state_gdp_tier) AS state_gdp_tier,
    MAX(state_population_tier) AS state_population_tier,
    MAX(distance_from_sp) AS distance_from_sp,
    
    -- Contar quantos customer_ids este cliente teve
    COUNT(DISTINCT customer_id) AS total_customer_ids,
    
    -- Lista de customer_ids (para debug)
    STRING_AGG(DISTINCT customer_id, ', ') AS customer_id_list,
    
    -- Metadata
    MAX(_loaded_at) AS _loaded_at
    
  FROM enriched
  GROUP BY customer_unique_id
)

-- Retornar versão individual (cada customer_id) E versão agregada
SELECT 
  e.*,
  cm.total_customer_ids,
  CASE 
    WHEN cm.total_customer_ids > 1 THEN TRUE 
    ELSE FALSE 
  END AS has_multiple_ids
  
FROM enriched e
LEFT JOIN customer_master cm 
  ON e.customer_unique_id = cm.customer_unique_id;


-- VIEW: Customer Master (1 linha por customer_unique_id)
CREATE OR REPLACE VIEW `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers_master` AS
SELECT 
  customer_unique_id,
  customer_state,
  customer_city,
  customer_zip_code_prefix,
  customer_region,
  customer_location_type,
  customer_metro_area,
  state_gdp_tier,
  state_population_tier,
  distance_from_sp,
  total_customer_ids,
  customer_id_list,
  _loaded_at
  
FROM (
  SELECT 
    customer_unique_id,
    MAX(customer_state) AS customer_state,
    MAX(customer_city) AS customer_city,
    MAX(customer_zip_code_prefix) AS customer_zip_code_prefix,
    MAX(customer_region) AS customer_region,
    MAX(customer_location_type) AS customer_location_type,
    MAX(customer_metro_area) AS customer_metro_area,
    MAX(state_gdp_tier) AS state_gdp_tier,
    MAX(state_population_tier) AS state_population_tier,
    MAX(distance_from_sp) AS distance_from_sp,
    COUNT(DISTINCT customer_id) AS total_customer_ids,
    STRING_AGG(DISTINCT customer_id, ', ') AS customer_id_list,
    MAX(_loaded_at) AS _loaded_at
    
  FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers`
  GROUP BY customer_unique_id
);


-- QUERIES DE VALIDAÇÃO

-- Sumário da tabela staging
SELECT 
  'Total Customer Records' AS metric,
  COUNT(*) AS value
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers`

UNION ALL

SELECT 
  'Unique Customers',
  COUNT(DISTINCT customer_unique_id)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers`

UNION ALL

SELECT 
  'Customers with Multiple IDs',
  COUNTIF(has_multiple_ids = TRUE)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers`

UNION ALL

SELECT 
  'Valid Zipcodes',
  COUNTIF(is_valid_zipcode = TRUE)
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers`

UNION ALL

SELECT 
  'From Capitals',
  COUNTIF(customer_location_type = 'Capital')
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers`

UNION ALL

SELECT 
  'From Sudeste',
  COUNTIF(customer_region = 'Sudeste')
FROM `${GCP_PROJECT_ID}.${GCP_DATASET_ID}.stg_customers`;


"""Constantes de domínio usadas pela aplicação."""

# Lista de especialistas que o modelo pode indicar. Mantida como uma única
# fonte de verdade: é usada tanto para restringir a resposta da IA (enum do
# JSON Schema) quanto para orientar a busca por locais no Nominatim.
ESPECIALISTAS = [
    "cardiologista",
    "dermatologista",
    "neurologista",
    "ortopedista",
    "ginecologista",
    "psicólogo",
    "otorrinolaringologista",
    "pediatra",
    "clínico geral",
    "endocrinologista",
    "urologista",
]

ESPECIALISTA_PADRAO = "clínico geral"

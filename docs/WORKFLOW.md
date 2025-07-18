# 🚀 Git Workflow & Development Process

## Flujo de Trabajo Completo del Proyecto

### 📋 Estrategia de Branching

El proyecto utiliza un **Git Flow modificado** optimizado para desarrollo ágil y calidad enterprise:

```
main (production-ready)
├── develop (integration branch)
├── feat/ui-compact-reports-20250718
├── feat/ml-sentiment-analysis-20250719
├── fix/story-parsing-bug-20250720
└── perf/memory-optimization-20250721
```

### 🔄 Estructura de Ramas

1. **`main`** - Rama principal de producción
   - Solo código 100% estable y testeado
   - Merge únicamente via Pull Request
   - Requiere revisión obligatoria

2. **`develop`** - Rama de integración
   - Punto de integración para features
   - Testing continuo
   - Merge a `main` cada sprint

3. **Feature Branches** - Ramas de características
   - Patrón: `feat/descripcion-fecha`
   - Vida corta: 1-3 días máximo
   - Merge a `develop` via PR

4. **Bugfix Branches** - Ramas de corrección
   - Patrón: `fix/descripcion-fecha`
   - Vida muy corta: horas/1 día
   - Merge directo a `develop` o `main`

### 🕒 Frecuencia de Merge

#### Merge Automático Diario
- **Features pequeñas**: Merge cada 24-48 horas
- **Features medianas**: Merge cada 3-5 días
- **Features grandes**: Dividir en sub-features más pequeñas

#### Merge a Main (Releases)
- **Releases menores**: Cada 1-2 semanas
- **Releases mayores**: Cada 3-4 semanas
- **Hotfixes**: Inmediato

### 🛠️ Flujo de Trabajo Paso a Paso

#### 1. Inicio de Feature
```bash
# Configurar git automation (una vez)
make git-setup

# Crear nueva feature branch
make branch-new
# o directamente:
git feat "Add compact HTML reports"
```

#### 2. Desarrollo Activo
```bash
# Mientras desarrollas
make test          # Ejecutar tests
make quality       # Verificar calidad
git add .
git commit -m "feat: implement data pagination"  # Auto-formateado
```

#### 3. Preparación para Merge
```bash
# Verificar que todo esté listo
make pr-ready      # Ejecuta CI completo
git push origin feat/compact-reports-20250718
```

#### 4. Pull Request
- Crear PR en GitHub
- Revisión automática por CI
- Revisión manual por equipo
- Merge automático si pasa todas las verificaciones

### 📊 Criterios de Merge

#### Merge Automático (Si cumple):
- ✅ Todos los tests pasan (88%+ success rate)
- ✅ Cobertura de código >80%
- ✅ Linting y type checking sin errores
- ✅ Security checks aprobados
- ✅ Documentación actualizada

#### Merge Manual (Requiere revisión):
- ⚠️ Cambios en arquitectura core
- ⚠️ Nuevas dependencias
- ⚠️ Cambios en API pública
- ⚠️ Modificaciones de configuración

### 🎯 Estrategia por Tipo de Cambio

#### Features (70% del desarrollo)
```bash
# Rama de vida corta: 1-3 días
git feat "Add ML sentiment analysis"
# Desarrollo iterativo
git commit -m "feat: implement TextBlob integration"
git commit -m "feat: add emotion detection"
git commit -m "feat: integrate with main analyzer"
# Merge rápido a develop
```

#### Optimizaciones (20% del desarrollo)
```bash
# Rama de vida muy corta: horas/1 día
git perf "Optimize memory usage in JSON parsing"
# Cambios focalizados
git commit -m "perf: implement streaming JSON parser"
git commit -m "perf: add memory profiling"
# Merge inmediato
```

#### Bugfixes (10% del desarrollo)
```bash
# Rama de vida inmediata: horas
git fix "Fix story count showing zero"
# Corrección directa
git commit -m "fix: correct Pydantic validation in Media model"
# Merge inmediato a develop o main
```

### 📈 Métricas de Flujo

#### Objetivos de Velocidad
- **Feature branches**: Max 3 días de vida
- **Commits por día**: 3-5 commits pequeños
- **PRs por semana**: 5-7 PRs
- **Merge rate**: 95% de PRs aprobados automáticamente

#### Métricas de Calidad
- **Test success rate**: >88% (actual)
- **Code coverage**: >80% (objetivo)
- **Security issues**: 0 críticos
- **Documentation**: 100% APIs documentadas

### 🔄 Ciclo de Vida de una Feature

```mermaid
graph TD
    A[Crear feature branch] --> B[Desarrollo iterativo]
    B --> C[Commits pequeños y frecuentes]
    C --> D[Tests y quality checks]
    D --> E[Push a origin]
    E --> F[Create Pull Request]
    F --> G[CI/CD Automático]
    G --> H[Code Review]
    H --> I[Merge a develop]
    I --> J[Deploy a staging]
    J --> K[Merge a main]
    K --> L[Deploy a production]
```

### 🚀 Comandos Esenciales

#### Setup Inicial
```bash
# Configurar entorno completo
make setup-dev

# Instalar git automation
make git-setup
```

#### Desarrollo Diario
```bash
# Crear nueva feature
make branch-new

# Verificar durante desarrollo
make quick-check

# Preparar para commit
make commit-ready

# Preparar para PR
make pr-ready
```

#### Monitoreo
```bash
# Ver historial de branches
make branch-history

# Estado actual
make status

# Configuración
make git-config
```

### 🎨 Estrategia de Releases

#### Versioning Automático
- **Patch** (0.2.X): Bugfixes, optimizaciones menores
- **Minor** (0.X.0): Nuevas features, mejoras
- **Major** (X.0.0): Cambios arquitectónicos, breaking changes

#### Release Schedule
- **Sprints**: 2 semanas
- **Minor releases**: Cada sprint
- **Major releases**: Cada 2-3 meses
- **Hotfixes**: Según necesidad

### 📋 Checklist de Desarrollo

#### Antes de Commitear
- [ ] Tests pasan localmente
- [ ] Linting sin errores
- [ ] Type checking correcto
- [ ] Documentación actualizada

#### Antes de PR
- [ ] CI completo pasa
- [ ] Cobertura mantenida
- [ ] Security checks OK
- [ ] Changelog actualizado

#### Antes de Merge
- [ ] Revisión de código
- [ ] Tests de integración
- [ ] Performance no degradada
- [ ] Compatibilidad verificada

### 🎯 Beneficios del Flujo

1. **Velocidad**: Merges rápidos y frecuentes
2. **Calidad**: Verificación automática continua
3. **Trazabilidad**: Historial completo de cambios
4. **Reversibilidad**: Fácil rollback si hay problemas
5. **Colaboración**: Flujo claro para todo el equipo

### 🔧 Personalización

El sistema es configurable via `.git-automation.json`:

```json
{
  "base_branch": "main",
  "auto_version": true,
  "merge_frequency": "daily",
  "require_tests": true,
  "auto_cleanup": true
}
```

### 📞 Soporte

Si tienes dudas sobre el flujo:
1. Consulta `make workflow-example`
2. Revisa `make branch-history`
3. Usa `make branch-new` para workflow interactivo

Este flujo garantiza desarrollo ágil manteniendo la calidad enterprise que caracteriza al proyecto.

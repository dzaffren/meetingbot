// MeetingBot — Container App deployment
// Updates an existing Azure Container App with a new image revision.
// All other Azure resources (OpenAI, Speech, AI Search, Cosmos DB, etc.)
// are assumed to be already provisioned — this file only manages the app.

@description('Name of the existing Container App')
param containerAppName string

@description('Name of the existing Container App Environment')
param containerAppEnvName string

@description('Resource group of the Container App (deployment scope)')
param location string = resourceGroup().location

@description('Full ACR image reference, e.g. myregistry.azurecr.io/meetingbot:sha-abc1234')
param image string

@description('Minimum number of replicas (0 = scale-to-zero)')
@minValue(0)
param minReplicas int = 0

@description('Maximum number of replicas')
@maxValue(10)
param maxReplicas int = 2

// ── Reference existing Container App Environment ───────────────────────────────
resource env 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: containerAppEnvName
}

// ── Container App ─────────────────────────────────────────────────────────────
// Uses 'existing' pattern: only the properties we declare here are modified.
// All secrets, env vars, and ingress config set during initial provisioning
// are preserved (managed outside this Bicep via Key Vault references).
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: env.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'meetingbot'
          image: image
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
      }
    }
  }
}

// ── Outputs ───────────────────────────────────────────────────────────────────
output fqdn string = containerApp.properties.configuration.ingress.fqdn
output latestRevisionName string = containerApp.properties.latestRevisionName

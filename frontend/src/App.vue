<template>
  <div id="app">
    <header class="app-header">
      <h1 class="app-title">Busca de Operadoras de Saúde</h1>
      <p class="app-subtitle">Pesquise por qualquer termo: nome, CNPJ, endereço, cidade, etc.</p>
    </header>
    
    <main class="app-main">
      <div class="search-container">
        <input 
          type="text" 
          v-model="termoBusca" 
          @input="buscarOperadoras" 
          placeholder="Digite qualquer termo para buscar..."
          class="search-input"
        />
        <button @click="buscarOperadoras" class="search-button">
          <span class="button-text">Buscar</span>
          <span class="button-icon">🔍</span>
        </button>
      </div>
      
      <div v-if="carregando" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Buscando operadoras...</p>
      </div>
      
      <div v-if="resultados.length > 0" class="results-container">
        <div class="results-header">
          <h2>{{ resultados.length }} resultado(s) encontrado(s)</h2>
          <div class="search-term">
            Termo buscado: <strong>"{{ termoBusca }}"</strong>
          </div>
        </div>
        
        <div class="results-list">
          <div v-for="(item, index) in resultados" :key="index" class="result-item">
            <div class="item-header">
              <h3>{{ item.Razao_Social || 'Operadora sem nome cadastrado' }}</h3>
              <span class="item-id">Registro ANS: {{ item.Registro_ANS || 'Não informado' }}</span>
            </div>
            
            <div class="item-highlights">
              <span v-if="item.Nome_Fantasia" class="highlight">
                Nome Fantasia: {{ item.Nome_Fantasia }}
              </span>
              <span v-if="containsTerm(item.CNPJ)" class="highlight">
                CNPJ: {{ formatCNPJ(item.CNPJ) }}
              </span>
              <span v-if="containsTerm(item.Modalidade)" class="highlight">
                Modalidade: {{ item.Modalidade }}
              </span>
              <span v-if="containsTerm(item.Cidade)" class="highlight">
                Localização: {{ item.Cidade }}/{{ item.UF }}
              </span>
            </div>
            
            <div class="item-details">
              <div class="detail-row" v-if="item.CNPJ">
                <span class="detail-label">CNPJ:</span>
                <span class="detail-value">{{ formatCNPJ(item.CNPJ) }}</span>
              </div>
              
              <div class="detail-row" v-if="item.Modalidade">
                <span class="detail-label">Modalidade:</span>
                <span class="detail-value">{{ item.Modalidade }}</span>
              </div>
              
              <div class="detail-row" v-if="item.Logradouro || item.Cidade">
                <span class="detail-label">Endereço:</span>
                <span class="detail-value">
                  {{ formatEndereco(item) }}
                </span>
              </div>
              
              <div class="detail-row" v-if="item.Telefone || item.Endereco_eletronico">
                <span class="detail-label">Contato:</span>
                <span class="detail-value">
                  <span v-if="item.Telefone">Tel: {{ item.Telefone }}</span>
                  <span v-if="item.Telefone && item.Endereco_eletronico"> | </span>
                  <span v-if="item.Endereco_eletronico">Email: {{ item.Endereco_eletronico }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else-if="termoBusca && !carregando" class="empty-state">
        <img src="https://cdn-icons-png.flaticon.com/512/4076/4076478.png" alt="Nada encontrado" class="empty-icon">
        <h3>Nenhum resultado encontrado para "{{ termoBusca }}"</h3>
        <p>Tente buscar por outros termos como nome, CNPJ ou cidade</p>
      </div>
      
      <div v-else class="welcome-state">
        <img src="https://cdn-icons-png.flaticon.com/512/3069/3069172.png" alt="Pesquisar" class="welcome-icon">
        <h3>Busque por operadoras de saúde</h3>
        <p>O sistema pesquisa em todos os campos simultaneamente</p>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      termoBusca: '',
      resultados: [],
      totalResultados: 0,
      carregando: false,
      erroBusca: '',
      timeout: null
    }
  },
  methods: {
    async buscarOperadoras() {
      if (this.timeout) clearTimeout(this.timeout);
      
      if (!this.termoBusca.trim()) {
        this.resultados = [];
        this.totalResultados = 0;
        return;
      }
      
      this.carregando = true;
      this.erroBusca = '';
      
      this.timeout = setTimeout(async () => {
        try {
          const response = await fetch(`http://localhost:5000/buscar?termo=${encodeURIComponent(this.termoBusca)}`);
          
          // Verifica se a resposta é JSON válido
          const contentType = response.headers.get('content-type');
          if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Resposta não é JSON válido');
          }
          
          const data = await response.json();
          
          if (!response.ok) {
            throw new Error(data.error || 'Erro na resposta do servidor');
          }
          
          // Verifica a estrutura esperada
          if (typeof data.total !== 'number' || !Array.isArray(data.resultados)) {
            throw new Error('Estrutura de dados inválida');
          }
          
          this.resultados = data.resultados;
          this.totalResultados = data.total;
          
        } catch (error) {
          console.error('Erro na busca:', error);
          this.erroBusca = error.message;
          this.resultados = [];
          this.totalResultados = 0;
        } finally {
          this.carregando = false;
        }
      }, 350);
    },
    formatCNPJ(cnpj) {
      if (!cnpj) return '';
      const nums = cnpj.toString().replace(/\D/g, '');
      return nums.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
    },
    formatEndereco(item) {
      const parts = [
        item.Logradouro,
        item.Numero,
        item.Complemento,
        item.Bairro,
        item.Cidade,
        item.UF
      ].filter(Boolean);
      return parts.join(', ');
    },
    containsTerm(value) {
      if (!value || !this.termoBusca) return false;
      return value.toString().toLowerCase().includes(this.termoBusca.toLowerCase());
    }
  }
}
</script>

<style>
:root {
  --primary-color: #42b983;
  --secondary-color: #35495e;
  --light-gray: #f8f9fa;
  --medium-gray: #e9ecef;
  --dark-gray: #6c757d;
  --white: #ffffff;
  --box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  --border-radius: 8px;
  --highlight-color: #fff9c4;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: var(--light-gray);
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: var(--secondary-color);
  color: var(--white);
  padding: 1.5rem 2rem;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-title {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.app-subtitle {
  opacity: 0.9;
  font-size: 1rem;
}

.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

.search-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input {
  flex: 1;
  padding: 0.8rem 1rem;
  border: 2px solid var(--medium-gray);
  border-radius: var(--border-radius);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.2);
}

.search-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1.5rem;
  background-color: var(--primary-color);
  color: var(--white);
  border: none;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-button:hover {
  background-color: #3aa876;
  transform: translateY(-1px);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid var(--medium-gray);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.results-container {
  margin-top: 2rem;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.results-header h2 {
  font-size: 1.3rem;
  color: var(--secondary-color);
}

.search-term {
  font-size: 0.9rem;
  color: var(--dark-gray);
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-item {
  background: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  padding: 1.5rem;
  transition: transform 0.3s ease;
}

.result-item:hover {
  transform: translateY(-2px);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
  border-bottom: 1px solid var(--medium-gray);
  padding-bottom: 0.5rem;
}

.item-header h3 {
  font-size: 1.2rem;
  color: var(--secondary-color);
  flex: 1;
  min-width: 60%;
}

.item-id {
  background-color: var(--primary-color);
  color: white;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.item-highlights {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.highlight {
  background-color: var(--highlight-color);
  padding: 0.3rem 0.6rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

.item-details {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-row {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.detail-label {
  font-weight: 600;
  color: var(--secondary-color);
  font-size: 0.9rem;
}

.detail-value {
  word-break: break-word;
}

.empty-state, .welcome-state {
  text-align: center;
  padding: 3rem 1rem;
  margin-top: 2rem;
  background: var(--white);
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
}

.empty-icon, .welcome-icon {
  width: 80px;
  height: 80px;
  margin-bottom: 1.5rem;
  opacity: 0.7;
}

.empty-state h3, .welcome-state h3 {
  color: var(--secondary-color);
  margin-bottom: 0.5rem;
}

.empty-state p, .welcome-state p {
  color: var(--dark-gray);
}

@media (max-width: 768px) {
  .app-main {
    padding: 1.5rem;
  }
  
  .item-details {
    grid-template-columns: 1fr;
  }
  
  .search-container {
    flex-direction: column;
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .item-id {
    align-self: flex-start;
  }
}
</style>
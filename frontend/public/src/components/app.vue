<template>
  <div id="app">
    <h1>Busca de Operadoras de Saúde</h1>
    <div class="search-container">
      <input
          type="text"
          v-model="termoBusca"
          @input="buscarOperadoras"
          placeholder="Digite para buscar..."
      />
      <button @click="buscarOperadoras">Buscar</button>
    </div>

    <div v-if="carregando" class="loading">Carregando...</div>

    <div v-if="resultados.length > 0" class="results">
      <h2>Resultados ({{ resultados.length }})</h2>
      <div v-for="(item, index) in resultados" :key="index" class="result-item">
        <h3>{{ item.Registro_ANS || 'N/A' }} - {{ item.Razao_Social || 'N/A' }}</h3>
        <p><strong>CNPJ:</strong> {{ item.CNPJ || 'N/A' }}</p>
        <p><strong>Modalidade:</strong> {{ item.Modalidade || 'N/A' }}</p>
        <p><strong>Endereço:</strong> {{ item.Endereco || 'N/A' }}</p>
      </div>
    </div>

    <div v-else-if="termoBusca && !carregando" class="no-results">
      Nenhum resultado encontrado para "{{ termoBusca }}"
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      termoBusca: '',
      resultados: [],
      carregando: false,
      timeout: null
    }
  },
  methods: {
    buscarOperadoras() {
      if (this.timeout) {
        clearTimeout(this.timeout);
      }

      if (!this.termoBusca.trim()) {
        this.resultados = [];
        return;
      }

      this.carregando = true;

      // Debounce para evitar muitas chamadas enquanto digita
      this.timeout = setTimeout(() => {
        fetch(`http://localhost:5000/buscar?termo=${encodeURIComponent(this.termoBusca)}`)
            .then(response => response.json())
            .then(data => {
              this.resultados = data;
              this.carregando = false;
            })
            .catch(error => {
              console.error('Erro:', error);
              this.carregando = false;
            });
      }, 300);
    }
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.search-container {
  margin: 20px 0;
  display: flex;
  gap: 10px;
}

input {
  padding: 10px;
  flex-grow: 1;
}

button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}

.result-item {
  background: #f5f5f5;
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 5px;
}

.loading {
  padding: 10px;
  color: #666;
}

.no-results {
  padding: 20px;
  text-align: center;
  color: #666;
}
</style>
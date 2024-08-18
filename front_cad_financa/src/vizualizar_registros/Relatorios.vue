<template>
    <div class="relatorios">
      <h2>Relatórios</h2>
      <div v-if="dados.length > 0">
        <!-- Exemplo: Listagem de relatórios ou gráfico -->
        <ul>
          <li v-for="(dado, index) in dados" :key="index">
            {{ dado.descricao }} - {{ dado.valor }} {{ dado.tipo }}
          </li>
        </ul>
      </div>
      <div v-else>
        <p>Nenhum dado disponível para os relatórios.</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      dados: {
        type: Array,
        required: true,
        default: () => []
      }
    }
  }
  </script>
  
  <style scoped>
  .relatorios {
    padding: 20px;
    background-color: #f9f9f9;
    border: 1px solid #ccc;
    border-radius: 10px;
  }
  
  ul {
    list-style: none;
    padding: 0;
  }
  
  li {
    margin: 5px 0;
  }
  </style>
  
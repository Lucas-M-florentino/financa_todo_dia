<template>
    <div class="metas">
      <h2>Metas Financeiras</h2>
      <div v-if="metas.length > 0">
        <ul>
          <li v-for="(meta, index) in metas" :key="index">
            {{ meta.descricao }} - Meta: {{ meta.valor }} - Alcançado: {{ meta.alcancado ? 'Sim' : 'Não' }}
          </li>
        </ul>
      </div>
      <div v-else>
        <p>Nenhuma meta definida.</p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      metas: {
        type: Array,
        required: true,
        default: () => []
      }
    }
  }
  </script>
  
  <style scoped>
  .metas {
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
  
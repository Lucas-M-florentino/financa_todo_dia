<template>
  <div id="finaceiro">
    <!-- Formulário de cadastro de transações -->
    <FormularioTransacao @adicionarTransacao="adicionarTransacao" />

    <!-- Seções de relatórios e metas organizadas em um grid flexível -->
    <section class="relatorios-metas">
      <Relatorios :dados="dadosRelatorios" />
      <Metas :metas="metasFinanceiras" />
    </section>
  </div>
</template>

<script>
// Importando subcomponentes
import FormularioTransacao from './FormularioTransacao.vue'
import Relatorios from '@/components/vizualizar_registros/Relatorios.vue'
import Metas from '@/components/vizualizar_registros/Metas.vue'
import api from '@/repository/api'

export default {
  components: {
    FormularioTransacao,
    Relatorios,
    Metas
  },
  data() {
    return {
      novaTransacao: {
        descricao: '',
        valor: 0,
        tipo: 'despesa'
      },
      dadosRelatorios: [],
      metasFinanceiras: [],
      transacoes: []
    }
  },
  methods: {
    async adicionarTransacao() {
      try {
        const response = await api.post('/transacoes', this.novaTransacao)
        this.transacoes.push(response.data)
        this.novaTransacao = { descricao: '', valor: 0, tipo: 'despesa' }
      } catch (error) {
        console.error('Erro ao adicionar transação:', error)
      }
    },
    async carregarTransacoes() {
      try {
        const response = await api.get('/transacoes')
        this.transacoes = response.data
      } catch (error) {
        console.error('Erro ao carregar transações:', error)
      }
    }
  },
  created() {
    this.carregarTransacoes()
  }
}
</script>

<style scoped>
#finaceiro {
  max-width: 1000px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  justify-content: space-between;
  margin: 0 auto;
  padding: 20px;
  gap: 20px;
}

.relatorios-metas {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.relatorios,
.metas {
  flex: 1;
  min-width: 300px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
  background-color: #f9f9f9;
}
</style>

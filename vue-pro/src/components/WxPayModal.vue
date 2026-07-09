<template>
  <div class="wx-pay-modal" v-if="visible">
    <div class="modal-mask" @click="closeModal"></div>
    <div class="modal-content">
      <div class="modal-header">
        <h3>微信支付</h3>
        <button class="close-btn" @click="closeModal">×</button>
      </div>
      <div class="modal-body">
        <div class="qrcode-container">
          <canvas ref="qrCanvas"></canvas>
        </div>
        <p class="payment-info">请使用微信扫描二维码完成支付</p>
        <p class="amount">支付金额：¥{{ (totalFee / 100).toFixed(2) }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import QRCode from 'qrcode'

export default {
  name: 'WxPayModal',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    payUrl: {
      type: String,
      required: true
    },
    totalFee: {
      type: Number,
      required: true
    }
  },
  watch: {
    payUrl: {
      immediate: true,
      handler(newUrl) {
        if (newUrl) {
          this.$nextTick(() => {
            this.generateQRCode()
          })
        }
      }
    }
  },
  methods: {
    closeModal() {
      this.$emit('update:visible', false)
    },
    async generateQRCode() {
      try {
        const canvas = this.$refs.qrCanvas
        if (canvas && this.payUrl) {
          await QRCode.toCanvas(canvas, this.payUrl, {
            width: 200,
            margin: 2,
            color: {
              dark: '#000000',
              light: '#ffffff'
            }
          })
        }
      } catch (error) {
        console.error('生成二维码失败:', error)
      }
    }
  }
}
</script>

<style scoped>
.wx-pay-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-content {
  position: relative;
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  z-index: 1001;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  text-align: center;
}

.qrcode-container {
  margin: 20px auto;
  padding: 15px;
  background: #fff;
  border-radius: 4px;
  display: inline-block;
}

.payment-info {
  margin: 15px 0;
  color: #666;
  font-size: 14px;
}

.amount {
  font-size: 18px;
  font-weight: bold;
  color: #ff6b00;
  margin: 10px 0;
}
</style>
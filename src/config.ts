import { createConfig,http } from '@wagmi/vue'
import { hederaMainnet, hederaTestnet } from './HederaChain'

export const config = createConfig({
  ssr: true,
  chains: [hederaTestnet,hederaMainnet],
  transports: {
    [hederaTestnet.id]: http(),
    [hederaMainnet.id]:http(),
  },
})

declare module '@wagmi/vue' {
  interface Register {
    config: typeof config
  }
}


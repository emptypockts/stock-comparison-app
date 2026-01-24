import { createConfig,http } from '@wagmi/vue'
import { hederaMainnet, hederaTestnet } from './HederaChain'
import {metaMask,walletConnect} from 'wagmi/connectors'

const projectId= import.meta.env.VITE_WALLETCONNECT_PROJECT_ID
if (!projectId){
  throw new Error('missing walletconnect project id')
  
}
export const config = createConfig({
  chains: [hederaTestnet,hederaMainnet],
  transports: {
    [hederaTestnet.id]: http(),
    [hederaMainnet.id]:http(),
  },
  connectors:[
    metaMask(),
    walletConnect({
      projectId:projectId,
      metadata:{
        name:'hbar donations',
        description: 'donate using hbar',
        url:window.location.origin,
        icons:[`${window.location.origin}/assets/dahoncho.png`]
      }
    })
  ]
})

declare module '@wagmi/vue' {
  interface Register {
    config: typeof config
  }
}


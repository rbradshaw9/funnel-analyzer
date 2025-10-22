'use client'

import { motion } from 'framer-motion'
import { FiLoader } from 'react-icons/fi'

export default function LoadingAnimation() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center py-20"
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        className="text-primary-600 mb-6"
      >
        <FiLoader className="text-6xl" />
      </motion.div>
      
      <h2 className="text-2xl font-semibold text-slate-900 mb-2">
        Analyzing Your Funnel...
      </h2>
      
      <p className="text-slate-600 text-center max-w-md">
        Our AI is scraping your pages and analyzing clarity, value, proof, design, and flow. 
        This usually takes 15-45 seconds.
      </p>
      
      <motion.div
        initial={{ width: '0%' }}
        animate={{ width: '100%' }}
        transition={{ duration: 30, ease: 'linear' }}
        className="mt-8 h-2 bg-primary-600 rounded-full max-w-md"
      />
    </motion.div>
  )
}

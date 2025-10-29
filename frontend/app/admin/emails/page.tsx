"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { FiMail, FiEdit, FiTrash2, FiEye, FiCode } from "react-icons/fi"
import AdminLayout from "@/components/AdminLayout"
import { useAuthStore } from "@/store/authStore"
import dynamic from "next/dynamic"
import "react-quill/dist/quill.snow.css"

// Dynamically import ReactQuill to avoid SSR issues
const ReactQuill = dynamic(() => import("react-quill"), { ssr: false })

interface EmailTemplate {
  id: number
  name: string
  subject: string
  html_content: string
  text_content: string
  description: string | null
  is_custom: boolean
  created_at: string
  updated_at: string | null
}

const TEMPLATE_NAMES = [
  { value: "magic_link", label: "Magic Link Login" },
  { value: "welcome", label: "Welcome Email" },
  { value: "analysis_complete", label: "Analysis Complete" },
  { value: "password_reset", label: "Password Reset" },
]

export default function EmailTemplatesPage() {
  const router = useRouter()
  const { token } = useAuthStore()
  const [templates, setTemplates] = useState<EmailTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [selectedTemplate, setSelectedTemplate] = useState<EmailTemplate | null>(null)
  const [editMode, setEditMode] = useState(false)
  const [previewMode, setPreviewMode] = useState(false)
  const [codeMode, setCodeMode] = useState(false)
  
  const [editSubject, setEditSubject] = useState("")
  const [editHtmlContent, setEditHtmlContent] = useState("")
  const [editTextContent, setEditTextContent] = useState("")
  const [saveLoading, setSaveLoading] = useState(false)

  // Quill editor modules
  const modules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ list: "ordered" }, { list: "bullet" }],
      [{ color: [] }, { background: [] }],
      ["link"],
      ["clean"],
    ],
  }

  useEffect(() => {
    if (!token) {
      router.push("/admin")
      return
    }
    loadTemplates()
  }, [token, router])

  const loadTemplates = async () => {
    try {
      setLoading(true)
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/email-templates`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!res.ok) {
        if (res.status === 403) {
          setError("Admin access required")
          return
        }
        throw new Error("Failed to load templates")
      }

      const data = await res.json()
      setTemplates(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadTemplate = async (templateName: string) => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/email-templates/${templateName}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )

      if (!res.ok) throw new Error("Failed to load template")

      const template: EmailTemplate = await res.json()
      setSelectedTemplate(template)
      setEditSubject(template.subject)
      setEditHtmlContent(template.html_content)
      setEditTextContent(template.text_content)
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    }
  }

  const saveTemplate = async () => {
    if (!selectedTemplate) return

    try {
      setSaveLoading(true)
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/email-templates/${selectedTemplate.name}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            subject: editSubject,
            html_content: editHtmlContent,
            text_content: editTextContent,
          }),
        }
      )

      if (!res.ok) throw new Error("Failed to save template")

      alert("Template saved successfully!")
      setEditMode(false)
      await loadTemplates()
      await loadTemplate(selectedTemplate.name)
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    } finally {
      setSaveLoading(false)
    }
  }

  const deleteTemplate = async (templateName: string) => {
    if (!confirm(`Revert ${templateName} to default template?`)) return

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/admin/email-templates/${templateName}`,
        {
          method: "DELETE",
          headers: { Authorization: `Bearer ${token}` },
        }
      )

      if (!res.ok) throw new Error("Failed to delete template")

      alert("Template reverted to default!")
      await loadTemplates()
      if (selectedTemplate?.name === templateName) {
        setSelectedTemplate(null)
        setEditMode(false)
      }
    } catch (err: any) {
      alert(`Error: ${err.message}`)
    }
  }

  if (error === "Admin access required") {
    return (
      <AdminLayout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          Access denied. Admin privileges required.
        </div>
      </AdminLayout>
    )
  }

  return (
    <AdminLayout>
      <div className="container mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Email Templates</h1>
          <p className="text-slate-600 mt-2">Customize transactional email templates</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Template List */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-slate-900 mb-4">Templates</h2>
              
              {loading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                </div>
              ) : (
                <div className="space-y-2">
                  {TEMPLATE_NAMES.map((template) => {
                    const customTemplate = templates.find((t) => t.name === template.value)
                    const isCustom = customTemplate?.is_custom || false

                    return (
                      <button
                        key={template.value}
                        onClick={() => loadTemplate(template.value)}
                        className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                          selectedTemplate?.name === template.value
                            ? "bg-blue-50 border border-blue-200"
                            : "hover:bg-slate-50 border border-transparent"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium text-slate-900">{template.label}</div>
                            <div className="text-xs text-slate-500">
                              {isCustom ? "Custom" : "Default"}
                            </div>
                          </div>
                          <FiMail className="h-4 w-4 text-slate-400" />
                        </div>
                      </button>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Template Editor/Preview */}
          <div className="lg:col-span-2">
            {selectedTemplate ? (
              <div className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-slate-900">
                    {TEMPLATE_NAMES.find((t) => t.value === selectedTemplate.name)?.label}
                  </h2>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setPreviewMode(!previewMode)
                        if (!previewMode) setCodeMode(false)
                      }}
                      className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg flex items-center gap-2"
                    >
                      <FiEye className="h-4 w-4" />
                      {previewMode ? "Edit" : "Preview"}
                    </button>
                    {editMode && !previewMode && (
                      <button
                        onClick={() => setCodeMode(!codeMode)}
                        className={`px-4 py-2 text-sm font-medium rounded-lg flex items-center gap-2 ${
                          codeMode
                            ? "bg-slate-100 text-slate-900"
                            : "text-slate-700 hover:bg-slate-100"
                        }`}
                      >
                        <FiCode className="h-4 w-4" />
                        {codeMode ? "Visual" : "Code"}
                      </button>
                    )}
                    {!editMode ? (
                      <button
                        onClick={() => setEditMode(true)}
                        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2"
                      >
                        <FiEdit className="h-4 w-4" />
                        Edit
                      </button>
                    ) : (
                      <>
                        <button
                          onClick={() => setEditMode(false)}
                          className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg"
                          disabled={saveLoading}
                        >
                          Cancel
                        </button>
                        <button
                          onClick={saveTemplate}
                          className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg"
                          disabled={saveLoading}
                        >
                          {saveLoading ? "Saving..." : "Save"}
                        </button>
                      </>
                    )}
                    {selectedTemplate.is_custom && (
                      <button
                        onClick={() => deleteTemplate(selectedTemplate.name)}
                        className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg flex items-center gap-2"
                      >
                        <FiTrash2 className="h-4 w-4" />
                        Revert
                      </button>
                    )}
                  </div>
                </div>

                {previewMode ? (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-slate-700 mb-2">Subject</h3>
                      <div className="p-3 bg-slate-50 rounded-lg text-sm text-slate-900">
                        {editSubject}
                      </div>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-slate-700 mb-2">HTML Preview</h3>
                      <div
                        className="p-4 border border-slate-200 rounded-lg bg-white"
                        dangerouslySetInnerHTML={{ __html: editHtmlContent }}
                      />
                    </div>
                  </div>
                ) : editMode ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Subject
                      </label>
                      <input
                        type="text"
                        value={editSubject}
                        onChange={(e) => setEditSubject(e.target.value)}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="block text-sm font-medium text-slate-700">
                          HTML Content
                        </label>
                        <span className="text-xs text-slate-500">
                          {codeMode ? "Raw HTML" : "Visual Editor"}
                        </span>
                      </div>
                      {codeMode ? (
                        <textarea
                          value={editHtmlContent}
                          onChange={(e) => setEditHtmlContent(e.target.value)}
                          rows={15}
                          className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                        />
                      ) : (
                        <div className="border border-slate-300 rounded-lg overflow-hidden">
                          <ReactQuill
                            theme="snow"
                            value={editHtmlContent}
                            onChange={setEditHtmlContent}
                            modules={modules}
                            className="bg-white"
                            style={{ minHeight: "300px" }}
                          />
                        </div>
                      )}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Plain Text Content
                      </label>
                      <textarea
                        value={editTextContent}
                        onChange={(e) => setEditTextContent(e.target.value)}
                        rows={6}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                        placeholder="Plain text version for email clients that don't support HTML"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-slate-700 mb-2">Subject</h3>
                      <div className="p-3 bg-slate-50 rounded-lg text-sm text-slate-900">
                        {selectedTemplate.subject}
                      </div>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-slate-700 mb-2">Status</h3>
                      <div className="text-sm text-slate-600">
                        {selectedTemplate.is_custom ? (
                          <span className="text-blue-600">Custom template (overrides default)</span>
                        ) : (
                          <span className="text-slate-500">Using default template from code</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                <FiMail className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <p className="text-slate-600">Select a template to view and edit</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AdminLayout>
  )
}

import { useState, useCallback } from "react";
import { REQUIRED_FIELDS, API_BASE } from "../utils/config";

const INITIAL_FORM = {
  district:    "",
  ward:        "",
  area:        "",
  propertyType:"",
  description: "",   // optional — để trống → backend dùng mock description
  street:      "",
  bedrooms:    "",
  bathrooms:   "",
};

export function useValuation() {
  const [city,    setCity]    = useState("hanoi");
  const [model,   setModel]   = useState("land");
  const [form,    setForm]    = useState(INITIAL_FORM);
  const [errors,  setErrors]  = useState({});
  const [result,  setResult]  = useState(null);
  const [loading, setLoading] = useState(false);
  const [toast,   setToast]   = useState(null);

  const updateField = useCallback((field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }, []);

  const switchModel = useCallback((m) => {
    setModel(m);
    setForm((prev) => ({ ...prev, propertyType: "" }));
    setErrors((prev) => { const next = { ...prev }; delete next.propertyType; return next; });
  }, []);

  const switchCity = useCallback((c) => {
    setCity(c);
    setForm((prev) => ({ ...prev, street: "", district: "", ward: "" }));
  }, []);

  const validate = useCallback(() => {
    const newErrors = {};
    REQUIRED_FIELDS.forEach((key) => {
      const val = form[key];
      if (!val || (typeof val === "string" && val.trim() === "")) {
        newErrors[key] = "Vui lòng điền thông tin này";
      }
    });
    if (form.area && isNaN(Number(form.area)))
      newErrors.area = "Diện tích phải là số";
    if (form.area && Number(form.area) <= 0)
      newErrors.area = "Diện tích phải lớn hơn 0";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [form]);

  const showToast = useCallback((message, type = "info") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3500);
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!validate()) {
      showToast("Vui lòng điền đầy đủ thông tin bắt buộc", "error");
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const payload = {
        city,
        modelType:    model,
        district:     form.district.trim(),
        ward:         form.ward.trim(),
        area:         parseFloat(form.area),
        propertyType: form.propertyType,
        // description: gửi chuỗi rỗng nếu user không nhập
        // backend sẽ tự sinh mock description
        description:  form.description.trim(),
        ...(form.street    ? { street:    form.street.trim() }        : {}),
        ...(form.bedrooms  ? { bedrooms:  parseInt(form.bedrooms) }   : {}),
        ...(form.bathrooms ? { bathrooms: parseInt(form.bathrooms) }  : {}),
      };

      const res = await fetch(`${API_BASE}/predict`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      showToast("Định giá hoàn tất!", "success");

    } catch (err) {
      console.error("Valuation error:", err);
      showToast(err.message || "Có lỗi xảy ra. Vui lòng thử lại.", "error");
    } finally {
      setLoading(false);
    }
  }, [city, model, form, validate, showToast]);

  const reset = useCallback(() => {
    setForm(INITIAL_FORM);
    setErrors({});
    setResult(null);
  }, []);

  return {
    city,    switchCity,
    model,   switchModel,
    form,    updateField,
    errors,
    result,
    loading,
    toast,
    handleSubmit,
    reset,
  };
}
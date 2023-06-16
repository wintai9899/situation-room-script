# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.
​
ActiveRecord::Schema.define(version: 2020_09_16_112503) do
​
  # These are extensions that must be enabled in order to support this database
  enable_extension "plpgsql"
​
  create_table "build_notes", force: :cascade do |t|
    t.bigint "ybd_build_id"
    t.bigint "user_id"
    t.text "body"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_build_notes_on_user_id"
    t.index ["ybd_build_id"], name: "index_build_notes_on_ybd_build_id"
  end
​
  create_table "daily_report_comments", id: :serial, force: :cascade do |t|
    t.text "body"
    t.integer "user_id"
    t.date "date"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["date"], name: "index_daily_report_comments_on_date"
    t.index ["user_id"], name: "index_daily_report_comments_on_user_id"
  end
​
  create_table "daily_report_notes", id: :serial, force: :cascade do |t|
    t.integer "user_id"
    t.text "body"
    t.date "date"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_daily_report_notes_on_user_id"
  end
​
  create_table "delayed_jobs", force: :cascade do |t|
    t.integer "priority", default: 0, null: false
    t.integer "attempts", default: 0, null: false
    t.text "handler", null: false
    t.text "last_error"
    t.datetime "run_at"
    t.datetime "locked_at"
    t.datetime "failed_at"
    t.string "locked_by"
    t.string "queue"
    t.datetime "created_at"
    t.datetime "updated_at"
    t.index ["priority", "run_at"], name: "delayed_jobs_priority"
  end
​
  create_table "identities", id: :serial, force: :cascade do |t|
    t.string "provider"
    t.string "uid"
    t.integer "user_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["user_id"], name: "index_identities_on_user_id"
  end
​
  create_table "imports", force: :cascade do |t|
    t.datetime "complete_at"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.string "name", null: false
    t.string "started_by", null: false
    t.bigint "user_id"
    t.index ["user_id"], name: "index_imports_on_user_id"
  end
​
  create_table "invocation_comments", force: :cascade do |t|
    t.text "body"
    t.bigint "user_id"
    t.bigint "invocation_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["invocation_id"], name: "index_invocation_comments_on_invocation_id"
    t.index ["user_id"], name: "index_invocation_comments_on_user_id"
  end
​
  create_table "invocation_identities", force: :cascade do |t|
    t.string "name", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end
​
  create_table "invocation_notes", force: :cascade do |t|
    t.text "body"
    t.bigint "user_id"
    t.bigint "invocation_id"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["invocation_id"], name: "index_invocation_notes_on_invocation_id"
    t.index ["user_id"], name: "index_invocation_notes_on_user_id"
  end
​
  create_table "invocations", force: :cascade do |t|
    t.text "command", null: false
    t.string "ytest_version", limit: 50, null: false
    t.integer "port", null: false
    t.boolean "bulk", null: false
    t.string "default_database", null: false
    t.string "default_user", null: false
    t.string "default_password", null: false
    t.string "admin_user", null: false
    t.string "admin_password", null: false
    t.datetime "started_at", null: false
    t.datetime "ended_at", null: false
    t.decimal "duration_ms", precision: 16, scale: 3, null: false
    t.string "executing_host", limit: 255, null: false
    t.string "executing_user", limit: 32, null: false
    t.string "executing_directory", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.bigint "ybd_build_id"
    t.bigint "import_id"
    t.bigint "machine_configuration_id"
    t.bigint "invocation_identity_id"
    t.string "ci_url"
    t.boolean "perf"
    t.index ["import_id"], name: "index_invocations_on_import_id"
    t.index ["invocation_identity_id"], name: "index_invocations_on_invocation_identity_id"
    t.index ["machine_configuration_id"], name: "index_invocations_on_machine_configuration_id"
    t.index ["ybd_build_id"], name: "index_invocations_on_ybd_build_id"
  end
​
  create_table "machine_configurations", force: :cascade do |t|
    t.string "hostname", null: false
    t.integer "worker_count", null: false
    t.integer "blade_count", null: false
    t.boolean "real_cluster", null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end
​
  create_table "perf200_sys_log_queries", force: :cascade do |t|
    t.bigint "perf_query_id"
    t.bigint "query_id", null: false
    t.bigint "parent_id"
    t.bigint "transaction_id", null: false
    t.string "plan_id", limit: 64
    t.string "status", limit: 255
    t.string "user_name", limit: 255
    t.string "application_name", limit: 255
    t.bigint "session_id"
    t.string "tags", limit: 255
    t.string "type", limit: 255
    t.datetime "submit_time"
    t.datetime "start_time"
    t.datetime "execution_time"
    t.datetime "end_time"
    t.decimal "planning_ms", precision: 18, scale: 3
    t.decimal "lock_ms", precision: 18, scale: 3
    t.decimal "queue_ms", precision: 18, scale: 3
    t.decimal "prepare_ms", precision: 18, scale: 3
    t.decimal "runtime_ms", precision: 18, scale: 3
    t.decimal "runtime_execution_ms", precision: 18, scale: 3
    t.decimal "total_ms", precision: 18, scale: 3
    t.bigint "io_read_bytes"
    t.bigint "io_write_bytes"
    t.bigint "io_spill_read_bytes"
    t.bigint "io_spill_write_bytes"
    t.bigint "io_network_bytes"
    t.decimal "avg_cpu_percent", precision: 9, scale: 2
    t.bigint "rows_inserted"
    t.bigint "rows_deleted"
    t.bigint "rows_returned"
    t.bigint "memory_bytes"
    t.bigint "memory_total_bytes"
    t.bigint "memory_estimated_bytes"
    t.bigint "memory_required_bytes"
    t.bigint "memory_granted_bytes"
    t.string "memory_estimate_confidence", limit: 16
    t.float "cost"
    t.string "priority", limit: 255
    t.text "query_text"
    t.string "pool_id", limit: 128
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["perf_query_id"], name: "index_perf200_sys_log_queries_on_perf_query_id"
  end
​
  create_table "perf200_sys_log_query_analyzes", force: :cascade do |t|
    t.bigint "perf_query_id"
    t.bigint "query_id", null: false
    t.integer "node_id", null: false
    t.bigint "rows_planned"
    t.bigint "rows_actual"
    t.bigint "memory_planned_bytes"
    t.bigint "memory_actual_bytes"
    t.bigint "io_read_bytes"
    t.bigint "io_write_bytes"
    t.bigint "io_network_bytes"
    t.bigint "io_network_count"
    t.decimal "runtime_ms", precision: 18, scale: 3
    t.decimal "skew"
    t.text "detail"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["perf_query_id"], name: "index_perf200_sys_log_query_analyzes_on_perf_query_id"
  end
​
  create_table "perf200_sys_log_query_explains", force: :cascade do |t|
    t.bigint "perf_query_id"
    t.text "plan_id", null: false
    t.integer "node_id", null: false
    t.bigint "parent_id"
    t.bigint "index", null: false
    t.text "type"
    t.text "workers"
    t.text "query_plan"
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
    t.index ["perf_query_id"], name: "index_perf200_sys_log_query_explains_on_perf_query_id"
  end
​
  create_table "perf500_sys_log_queries", force: :cascade do |t|
    t.bigint "perf_query_id"
    t.bigint "query_id", null: false
    t.bigint "session_id"
    t.bigint "transaction_id", null: false
    t.string "plan_id", limit: 64
    t.string "state", limit: 50
    t.string "username", limit: 128
    t.string "application_name", limit: 128
    t.string "database_name", limit: 128
    t.string "type", limit: 128
    t.string "tags", limit: 128
    t.string "error_code", limit: 5
    t.string "error_message", limit: 255
    t.string "query_text", limit: 60000
    t.string "pool_id", limit: 128
    t.string "priority", limit: 30
    t.bigint "slot"
    t.bigint "num_workers"
    t.string "longest_worker_id", limit: 38
    t.bigint "compile_percent"
    t.bigint "cpu_percent"
    t.bigint "cpu_percent_max"
    t.bigint "num_restart"
    t.bigint "num_error"
    t.decimal "parse_ms", precision: 18, scale: 3
    t.decimal "wait_parse_ms", precision: 18, scale: 3
    t.decimal "wait_lock_ms", precision: 18, scale: 3
    t.decimal "plan_ms", precision: 18, scale: 3
    t.decimal "wait_plan_ms", precision: 18, scale: 3
    t.decimal "assemble_ms", precision: 18, scale: 3
    t.decimal "wait_assemble_ms", precision: 18, scale: 3
    t.decimal "compile_ms", precision: 18, scale: 3
    t.decimal "wait_compile_ms", precision: 18, scale: 3
    t.decimal "acquire_resources_ms", precision: 18, scale: 3
    t.decimal "run_ms", precision: 18, scale: 3
    t.decimal "wait_run_cpu_ms", precision: 18, scale: 3
    t.decimal "wait_run_io_ms", precision: 18, scale: 3
    t.decimal "wait_run_spool_ms", precision: 18, scale: 3
    t.decimal "client_ms", precision: 18, scale: 3
    t.decimal "wait_client_ms", precision: 18, scale: 3
    t.decimal "total_ms", precision: 18, scale: 3
    t.decimal "cancel...
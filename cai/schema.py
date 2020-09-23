schema_def = [
# table: report_prediction
    """
CREATE TABLE report_prediction(
    report_id integer NOT NULL,
    prediction double precision NOT NULL,
    CONSTRAINT report_prediction_pkey PRIMARY KEY (report_id)
);
    """,
# table: report_prediction_history
    """
CREATE SEQUENCE report_prediction_history_seq;
CREATE TABLE report_prediction_history AS TABLE report_prediction WITH NO DATA;
ALTER TABLE report_prediction_history
    ADD COLUMN id integer default nextval('report_prediction_history_seq'),
    ADD COLUMN history_change_time timestamptz DEFAULT now(),
    ADD COLUMN history_change_type character varying(16) NULL,
    ADD PRIMARY KEY (id);
    """,
# function: report_prediction_trigger
    """
CREATE FUNCTION report_prediction_trigger() RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE'
  THEN
    INSERT INTO report_prediction_history (report_id, prediction, history_change_type)
      VALUES (NEW.report_id, NEW.prediction, TG_OP);
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE 'plpgsql' SECURITY DEFINER;
    """,
# trigger: prediction_history
    """
CREATE TRIGGER prediction_history AFTER INSERT OR UPDATE ON report_prediction
FOR EACH ROW EXECUTE PROCEDURE report_prediction_trigger();
    """,
]


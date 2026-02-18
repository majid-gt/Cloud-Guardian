class CloudState:
    def __init__(self):
        # ---------- INVENTORY ----------
        # Raw discovered resources
        self.inventory = {
            "ec2": {},
            "ebs": {},
            "eip": {},
            "rds": {},
            "s3": {},
            "security_groups": {},
            "iam_users": {},
            "snapshots": {}
        }

        # ---------- METRICS ----------
        # Utilization & behavioral data
        self.metrics = {
            "ec2_cpu": {},
            "rds_cpu": {},
            "rds_connections": {},
            "lb_requests": {},
            "s3_last_access_days": {},
            "iam_last_used_days": {}
        }

        # ---------- RELATIONS ----------
        # Dependency graph
        self.relations = {
            "instance_volumes": {},
            "volume_instance": {},
            "instance_eip": {},
            "instance_sg": {}
        }

        # ---------- COMPUTE CLASSIFICATION ----------
        # Active / idle status
        self.compute_status = {
            "ec2": {},
            "rds": {}
        }

        # ---------- FINDINGS ----------
        self.findings = {
            "cost": [],
            "efficiency": [],
            "security": []
        }

    # ======================================================
    # INVENTORY METHODS
    # ======================================================

    def add_resource(self, service, resource_id, data):
        if service in self.inventory:
            self.inventory[service][resource_id] = data

    # ======================================================
    # METRIC METHODS
    # ======================================================

    def add_metric(self, metric_type, resource_id, value):
        if metric_type in self.metrics:
            self.metrics[metric_type][resource_id] = value

    # ======================================================
    # RELATION METHODS
    # ======================================================

    def add_relation(self, relation_type, source, target):
        if relation_type in self.relations:
            if source not in self.relations[relation_type]:
                self.relations[relation_type][source] = []
            self.relations[relation_type][source].append(target)

    # ======================================================
    # COMPUTE STATUS METHODS
    # ======================================================

    def set_compute_status(self, service, resource_id, status):
        if service in self.compute_status:
            self.compute_status[service][resource_id] = status

    # ======================================================
    # FINDING METHODS
    # ======================================================

    def add_finding(self, category, finding):
        if category in self.findings:
            self.findings[category].append(finding)

    # ======================================================
    # SUMMARY METHODS
    # ======================================================

    def get_total_findings(self):
        return sum(len(v) for v in self.findings.values())

    def get_all_findings(self):
        return self.findings
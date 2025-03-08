class NewModel(models.Model):
    _name = 'new.model'
    _description = 'New Model'

    name = fields.Char(string='Name', required=True)